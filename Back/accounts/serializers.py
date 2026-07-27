from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, StatusHistory

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
    email = serializers.EmailField(required=True)
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
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'first_name', 'last_name',
            'role', 'status', 'telephone', 'custom_permissions'
        ]
    
    def validate_role(self, value):
        """Valider que le créateur peut créer ce rôle"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Utilisateur non authentifié")
        
        creator = request.user
        
        # Super admin peut créer n'importe quel rôle
        if creator.role == 'SUPER_ADMIN':
            return value
        
        # Chef peut créer seulement des agents
        if creator.role == 'CHEF_FACTURATION' and value == 'AGENT_FACTURATION':
            return value
        
        raise serializers.ValidationError(
            f"Vous n'avez pas la permission de créer un utilisateur avec le rôle {value}"
        )
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        
        # Associer le créateur
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user.created_by = request.user
        
        user.save()
        return user
