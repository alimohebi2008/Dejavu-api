from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    role = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Role.objects.all(),
        required=False
    )
    role_detail = RoleSerializer(source='role', many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'is_active', 'role', 'role_detail', 'image', 'phone_number'
        ]
        read_only_fields = ['last_login', 'date_joined']

    def validate_password(self, value):
        user = self.instance or User()
        for attribute in ('username', 'first_name', 'last_name', 'email'):
            if attribute in self.initial_data:
                setattr(user, attribute, self.initial_data[attribute])
        validate_password(value, user=user)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        roles = validated_data.pop('role', [])
        user = User(**validated_data)
        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)
        user.save()
        user.role.set(roles)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password is not None:
            user.set_password(password)
            user.save(update_fields=['password'])
        return user


