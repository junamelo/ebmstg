from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

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
            
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.est_actif:
                    return Response({
                        'error': 'Compte désactivé'
                    }, status=status.HTTP_403_FORBIDDEN)
                
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
