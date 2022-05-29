from django.urls import path
from .views import *

urlpatterns = [
    path('test', test.as_view()),
    path('register/', UserRegisterView.as_view(), name='create-user'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('update/', UserUpdateView.as_view(), name='update-user'),
    path('listuser/', ListUserView.as_view(), name='list-user'),
    path('emailotpverification/', EmailOtpVerificationView.as_view(), name='user-email-verification'),
    path('mobileotpverification/', MobileOtpVerificationView.as_view(), name='user-mobile-verification'),
]