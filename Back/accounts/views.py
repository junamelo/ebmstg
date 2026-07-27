from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from .models import User, StatusHistory, ROLE_PERMISSIONS
from .serializers import (
    UserSerializer, UserListSerializer, RegisterSerializer, LoginSerializer,
    ChangeStatusSerializer, PermissionSerializer, StatusHistorySerializer,
    CreateUserSerializer
)

class RegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    @extend_schema(
        summary='Inscription utilisateur',
        description='Crée un nouvel compte utilisateur',
        responses={
            201: OpenApiResponse(description='Utilisateur créé avec succès'),
            400: OpenApiResponse(description='Données invalides'),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    @extend_schema(
        summary='Connexion utilisateur',
        description='Authentifie un utilisateur et retourne un token JWT',
        responses={
            200: OpenApiResponse(description='Connexion réussie'),
            401: OpenApiResponse(description='Email ou mot de passe incorrect'),
            403: OpenApiResponse(description='Compte désactivé'),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Chercher l'utilisateur par email
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                return Response({
                    'error': 'Email ou mot de passe incorrect'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Vérifier le statut avant d'authentifier
            if user.status != 'ACTIF':
                return Response({
                    'error': f'Compte {user.status.lower()}. Contactez un administrateur.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.est_actif:
                    return Response({
                        'error': 'Compte désactivé'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Enregistrer l'IP de connexion
                user.last_login_ip = request.META.get('REMOTE_ADDR')
                user.save(update_fields=['last_login_ip'])
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    @extend_schema(
        summary='Profil utilisateur',
        description='Retourne les informations de l\'utilisateur connecté',
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description='Non authentifié'),
        }
    )
    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion complète des utilisateurs (Admin/Chef)
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return CreateUserSerializer
        return UserSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Super admin voit tout
        if user.role == 'SUPER_ADMIN':
            return User.objects.all().order_by('-date_creation')
        
        # Chef voit ses agents + lui-même
        if user.role == 'CHEF_FACTURATION':
            return User.objects.filter(
                Q(created_by=user) | Q(id=user.id)
            ).order_by('-date_creation')
        
        # Autres rôles voient seulement eux-mêmes
        return User.objects.filter(id=user.id)
    
    def create(self, request, *args, **kwargs):
        """Créer un nouvel utilisateur"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Changer le statut d'un utilisateur"""
        target_user = self.get_object()
        
        # Vérifier les permissions
        if not request.user.can_manage_user(target_user):
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier cet utilisateur'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = target_user.status
        new_status = serializer.validated_data['new_status']
        reason = serializer.validated_data['reason']
        end_date = serializer.validated_data.get('end_date')
        
        # Enregistrer l'historique
        StatusHistory.objects.create(
            user=target_user,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            reason=reason,
            end_date=end_date
        )
        
        # Mettre à jour l'utilisateur
        target_user.status = new_status
        target_user.status_changed_at = timezone.now()
        target_user.status_changed_by = request.user
        target_user.status_reason = reason
        target_user.status_end_date = end_date
        target_user.save()
        
        # TODO: Envoyer notification email si demandé
        
        return Response({
            'message': 'Statut modifié avec succès',
            'user': UserSerializer(target_user).data
        })
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """Voir l'historique des changements de statut"""
        target_user = self.get_object()
        
        if not request.user.can_manage_user(target_user) and request.user.id != target_user.id:
            return Response(
                {'error': 'Vous n\'avez pas la permission de voir cet historique'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        history = target_user.status_history.all()
        serializer = StatusHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_permission(self, request, pk=None):
        """Ajouter ou retirer une permission personnalisée"""
        target_user = self.get_object()
        
        # Seul super admin peut gérer les permissions
        if request.user.role != 'SUPER_ADMIN':
            return Response(
                {'error': 'Seul un super admin peut gérer les permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        permission = serializer.validated_data['permission']
        action = serializer.validated_data['action']
        
        if action == 'add':
            if permission not in target_user.custom_permissions:
                target_user.custom_permissions.append(permission)
                message = f'Permission "{permission}" ajoutée'
        else:  # remove
            if permission in target_user.custom_permissions:
                target_user.custom_permissions.remove(permission)
                message = f'Permission "{permission}" retirée'
            else:
                return Response(
                    {'error': 'Cette permission n\'existe pas pour cet utilisateur'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        target_user.save()
        
        return Response({
            'message': message,
            'user': UserSerializer(target_user).data
        })
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Voir toutes les permissions d'un utilisateur"""
        target_user = self.get_object()
        
        # Permissions du rôle
        role_permissions = ROLE_PERMISSIONS.get(target_user.role, [])
        
        # Permissions personnalisées
        custom_permissions = target_user.custom_permissions
        
        return Response({
            'role': target_user.role,
            'role_permissions': role_permissions,
            'custom_permissions': custom_permissions,
            'all_permissions': list(set(role_permissions + custom_permissions))
        })
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Réinitialiser le mot de passe d'un utilisateur"""
        target_user = self.get_object()
        
        if not request.user.can_manage_user(target_user):
            return Response(
                {'error': 'Vous n\'avez pas la permission de réinitialiser ce mot de passe'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_password = request.data.get('new_password')
        if not new_password:
            return Response(
                {'error': 'Le nouveau mot de passe est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        target_user.set_password(new_password)
        target_user.save()
        
        # TODO: Envoyer email avec nouveau mot de passe
        
        return Response({
            'message': 'Mot de passe réinitialisé avec succès'
        })
