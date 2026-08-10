from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from .models import User, StatusHistory

MOOV_PREFIXES = ('78', '79', '96', '97', '98', '99')


def normalize_phone(value):
    return ''.join(ch for ch in str(value or '') if ch.isdigit())


def validate_moov_phone(value, required=False):
    numero = normalize_phone(value)
    if not numero and not required:
        return ''
    if len(numero) != 8 or not numero.startswith(MOOV_PREFIXES):
        raise serializers.ValidationError(
            f"Numéro invalide. Format attendu : 8 chiffres avec préfixe Moov ({', '.join(MOOV_PREFIXES)})."
        )
    return numero

class UserSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    status_changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'role', 'status',
            'telephone', 'est_actif', 'custom_permissions',
            'status_changed_at', 'status_reason', 'status_end_date',
            'created_by', 'created_by_name', 'status_changed_by_name',
            'date_creation', 'date_modification', 'last_login', 'last_login_ip'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification', 'last_login']

    def validate_telephone(self, value):
        return validate_moov_phone(value, required=False)
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_status_changed_by_name(self, obj):
        if obj.status_changed_by:
            return f"{obj.status_changed_by.first_name} {obj.status_changed_by.last_name}"
        return None


class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes"""
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'status',
            'telephone', 'est_actif', 'created_by_name',
            'date_creation', 'last_login'
        ]
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class ChangeStatusSerializer(serializers.Serializer):
    """Serializer pour changer le statut d'un utilisateur"""
    new_status = serializers.ChoiceField(choices=User.STATUS_CHOICES)
    reason = serializers.CharField(required=True, max_length=500)
    end_date = serializers.DateTimeField(required=False, allow_null=True)
    send_notification = serializers.BooleanField(default=True)


class PermissionSerializer(serializers.Serializer):
    """Serializer pour gérer les permissions"""
    permission = serializers.CharField(required=True)
    action = serializers.ChoiceField(choices=['add', 'remove'])


class StatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StatusHistory
        fields = [
            'id', 'user', 'user_name', 'old_status', 'new_status',
            'changed_by', 'changed_by_name', 'changed_at', 'reason', 'end_date'
        ]
    
    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return f"{obj.changed_by.first_name} {obj.changed_by.last_name}"
        return "Système"
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class LoginSerializer(serializers.Serializer):
    # Le champ conserve le nom "email" pour compatibilité avec le frontend,
    # mais accepte aussi un MSISDN/username comme identifiant de connexion.
    email = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'telephone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Associer le créateur
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user.created_by = request.user
            user.save()
        return user


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur par admin/chef"""
    password = serializers.CharField(write_only=True, required=True)
    force_password_change = serializers.BooleanField(default=True, write_only=True)
    send_email = serializers.BooleanField(default=True, write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'first_name', 'last_name',
            'role', 'status', 'telephone', 'custom_permissions',
            'force_password_change', 'send_email'
        ]
    
    def validate_telephone(self, value):
        return validate_moov_phone(value, required=False)

    def validate_role(self, value):
        """Valider que le créateur peut créer ce rôle"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Utilisateur non authentifié")
        
        creator = request.user
        
        # Super admin peut créer n'importe quel rôle
        if creator.role == 'SUPER_ADMIN':
            return value
        
        # Chef peut créer des agents, commerciaux, payeurs et employés
        if creator.role == 'CHEF_FACTURATION' and value in ['AGENT_FACTURATION', 'COMMERCIAL', 'PAYEUR', 'EMPLOYE']:
            return value
        
        # Agent peut créer des payeurs, employés et commerciaux
        if creator.role == 'AGENT_FACTURATION' and value in ['PAYEUR', 'EMPLOYE', 'COMMERCIAL']:
            return value
        
        raise serializers.ValidationError(
            f"Vous n'avez pas la permission de créer un utilisateur avec le rôle {value}"
        )
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        force_password_change = validated_data.pop('force_password_change', True)
        send_email = validated_data.pop('send_email', True)
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        
        # Associer le créateur
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user.created_by = request.user
        
        user.save()

        # Lier/initialiser le profil commercial si rôle COMMERCIAL
        if user.role == 'COMMERCIAL':
            from billing.models import Commercial

            profil = Commercial.objects.filter(user=user).first()
            if not profil:
                profil = Commercial.objects.filter(user__isnull=True).filter(
                    Q(matricule=user.username) | Q(email=user.email)
                ).first()

            if profil:
                profil.user = user
                if not profil.telephone and user.telephone:
                    profil.telephone = user.telephone
                profil.save()
            else:
                Commercial.objects.create(
                    user=user,
                    nom=user.last_name or user.username,
                    prenom=user.first_name or 'Commercial',
                    matricule=user.username,
                    telephone=user.telephone or '',
                    email=user.email or ''
                )
        
        # TODO: Gérer force_password_change (ajouter champ au modèle si nécessaire)
        # TODO: Envoyer email si send_email=True
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer son propre mot de passe"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    two_factor_code = serializers.RegexField(r'^\d{6}$', required=False, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Les mots de passe ne correspondent pas"})
        return attrs


class TwoFactorSetupSerializer(serializers.Serializer):
    """Le mot de passe courant évite qu'une session volée active son propre TOTP."""
    password = serializers.CharField(required=True, write_only=True)


class TwoFactorCodeSerializer(serializers.Serializer):
    code = serializers.RegexField(r'^\d{6}$', write_only=True)


class TwoFactorDisableSerializer(TwoFactorCodeSerializer):
    password = serializers.CharField(required=True, write_only=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer pour réinitialiser le mot de passe d'un utilisateur (admin/chef)"""
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    force_change = serializers.BooleanField(default=True)
    send_email = serializers.BooleanField(default=True)


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer pour rafraîchir le token JWT"""
    refresh = serializers.CharField(required=True)
