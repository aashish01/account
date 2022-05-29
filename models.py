from django.db import models
from django.db.models.signals import pre_save
from .utils import username_generator, hash_password, otp_generator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db.models import Q


class UserManager(BaseUserManager):
    def _create_user(self, mobile_number, password, **extra_fields):
        if not mobile_number:
            raise ValueError("Mobile number is required.")

        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, mobile_number, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(mobile_number, password, **extra_fields)

 
    def create_superuser(self, mobile_number, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(mobile_number, password, **extra_fields)


obj = BaseUserManager()


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(blank=False, max_length=255, help_text="First name of User.")
    last_name = models.CharField(blank=False, max_length=255, help_text="Last name of User.")
    username = models.CharField(blank=True, max_length=255, unique=True, help_text="Username of User.")
    email = models.EmailField(blank=False, unique=True, max_length=255, help_text="Email of User.")
    mobile_number = models.CharField(blank=False, unique=True, max_length=10, help_text="Mobile number of User.")
    delivery_address = models.CharField(blank=False, max_length=255, help_text="Delivery address of User.")
    is_mobile_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    USERNAME_FIELD = "mobile_number"


    objects = UserManager()

    def save(self, *args, **kwargs):
        self.email = obj.normalize_email(self.email)
        self.first_name = self.first_name.capitalize()    
        self.last_name = self.last_name.capitalize()

        super(User, self).save(*args, **kwargs)



class MobileOtp(models.Model):

    otp_user_mobile = models.OneToOneField(User, blank=False, on_delete=models.CASCADE, help_text="User.")
    otp = models.CharField(blank=False, max_length=5, help_text="User's OTP.")

    def __str__(self):
        return self.otp_user_mobile.mobile_number + ' ' + self.otp


class EmailOtp(models.Model):

    otp_user_email = models.OneToOneField(User, blank=False, on_delete=models.CASCADE, help_text="User.")
    otp = models.CharField(blank=False, max_length=5, help_text="User's OTP.")

    def __str__(self):
        return self.otp_user_email.email + ' ' + self.otp


        

pre_save.connect(username_generator, sender=User)
pre_save.connect(hash_password, sender=User)
pre_save.connect(otp_generator, sender=EmailOtp)
pre_save.connect(otp_generator, sender=MobileOtp)