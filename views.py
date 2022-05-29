from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import User, EmailOtp, MobileOtp
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import auth
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
import requests



class test(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {'message': 'asdasd', 'user': request.user.mobile_number}
        return Response(content)


def get_token_from_db(otp_queryset):
    for i in otp_queryset:
        otp = i.otp
    return otp


def send_otp_to_email(email):
    user = User.objects.get(email=email)
    EmailOtp.objects.create(otp_user_email=user)
    queryset = EmailOtp.objects.filter(otp_user_email=user)
    otp = get_token_from_db(queryset)
    send_mail(
    'Khaanpin Account email verification.',
    'Your OTP for email verification is: '+str(otp),
    settings.EMAIL_HOST_USER,
    [email],
    fail_silently=False,
    )

def send_otp_to_mobile(mobile_number):
    user = User.objects.get(mobile_number=mobile_number)
    MobileOtp.objects.create(otp_user_mobile=user)
    queryset = MobileOtp.objects.filter(otp_user_mobile=user)
    otp = get_token_from_db(queryset)
    url = "https://eg3.egms.pro/api/sendbulk/"
    payload={'client_bulk_num': 9615555444,
    'sms': 'Your OTP for Khanpin account mobile verfication is: '+str(otp),
    'numbers': int(mobile_number)}
    headers = {
    'Authorization': 'Token 672abdf9eeedb7203b1e2cd973709035c6b903e2'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


#send otp to email for registration
class UserRegisterView(APIView):
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            new_user_email = request.data['email']
            new_user_mobile_number = request.data['mobile_number']
            send_otp_to_email(new_user_email)
            # send_otp_to_mobile(new_user_mobile_number)            
            return Response(
                {
                    'error': False,
                    'data': serializer.data,
                    'message': 'User has successfully been created.',
                    'status': status.HTTP_201_CREATED
                },
                status=status.HTTP_201_CREATED)

        return Response(
            {
                'error': True,
                'message': serializer.errors,
                'status': status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST)



#check otp for verification sent to email
class EmailOtpVerificationView(APIView):
    def post(self, request):
        try:
            otp = request.data['otp']
            check_user_otp = EmailOtp.objects.filter(otp=otp)

            for i in check_user_otp:
                temp = i.otp_user_email
                
            user = User.objects.get(mobile_number=temp)
            user_email = user.email
            if user_email:
                if user.is_email_verified == True:
                    return Response({
                        'error': True,
                        'message': 'Email is already verified.',
                        'status': status.HTTP_400_BAD_REQUEST 
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.is_email_verified = True
                user.save()
                check_user_otp.delete()
                return Response({
                    'error': False,
                    'message': 'Email has been verified.',
                    'status': status.HTTP_202_ACCEPTED
                }, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({
                        'error': True,
                        'message': "Otp did not match.",
                        'status': status.HTTP_400_BAD_REQUEST 
                    }, status=status.HTTP_400_BAD_REQUEST)



class MobileOtpVerificationView(APIView):
    def post(self, request):
        try:
            otp = request.data['otp']
            print(otp)
            check_user_otp = MobileOtp.objects.filter(otp=otp)

            for i in check_user_otp:
                temp = i.otp_user_mobile
                

            print(temp)
            user = User.objects.get(mobile_number=temp)
            if user:
                if user.is_mobile_verified == True:
                    return Response({
                        'error': True,
                        'message': 'Mobile number is already verified.',
                        'status': status.HTTP_400_BAD_REQUEST 
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.is_mobile_verified = True
                user.save()
                check_user_otp.delete()
                return Response({
                    'error': False,
                    'message': 'Mobile number has been verified.',
                    'status': status.HTTP_202_ACCEPTED
                }, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({
                        'error': True,
                        'message': "Otp did not match.",
                        'status': status.HTTP_400_BAD_REQUEST 
                    }, status=status.HTTP_400_BAD_REQUEST)
        




class UserLoginView(APIView):

    def post(self, request):
        mobile_number = request.data['mobile_number']
        password = request.data['password']

        user = auth.authenticate(mobile_number=mobile_number, password=password)
        if user is not None:
            auth.login(request, user)
            tokens = self.get_tokens_for_user(user)
            return Response({
                "error": False,
                "message": "Successfully Logged in.",
                "refresh token": tokens['refresh'],
                "access token": tokens['access'],
                "status": status.HTTP_202_ACCEPTED
            }, status=status.HTTP_202_ACCEPTED)
        return Response({
            'error': True,
            'message': 'Credentials did not match.',
            'status': status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }



class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        auth.logout(request)
        return Response({
            "error": False,
            "message": "Successfully Logged out.",
            "status": status.HTTP_202_ACCEPTED
        }, status=status.HTTP_202_ACCEPTED)
  



class UserUpdateView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def patch(self, request):
       
        try:
            user_id = request.data['user_id']
            user_obj = User.objects.get(id=user_id)
            serializer = UserUpdateSerializer(user_obj,
                                                data=request.data,
                                                partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "error": False,
                        "data": serializer.data,
                        "message": "User can been successfully updated.",
                        "status": status.HTTP_201_CREATED
                    },
                    status=status.HTTP_201_CREATED)
        except:
            return Response(
                {
                    "error": True,
                    "message": "User not found.",
                    "status": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST)





class ListUserView(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = User.objects.all()