from .models import User
from rest_framework import serializers, status


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'mobile_number', 'email',
            'password', 'confirm_password', 'delivery_address'
        ]
        read_only_fields = ['confirm_password']

    def create(self, validated_data):

        if not validated_data.get('password') or not validated_data.get(
                'confirm_password'):
            error_null_pass = {
                'error': True,
                'message': "Password or confirm password cannot be blank.",
                'status': status.HTTP_400_BAD_REQUEST
            }
            raise serializers.ValidationError(error_null_pass)

        if validated_data.get('password') != validated_data.get(
                'confirm_password'):
            error_mismatch_pass = {
                'error': True,
                'message': "Password and confirm password do not match.",
                'status': status.HTTP_400_BAD_REQUEST
            }
            raise serializers.ValidationError(error_mismatch_pass)

        user = User.objects.create_user(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            mobile_number=validated_data.get('mobile_number'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            delivery_address=validated_data.get('delivery_address'))
        return user



class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name','last_name','username','delivery_address']



class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ['password',]


