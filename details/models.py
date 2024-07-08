from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    
# email='ola@mide.com', first_name='jeff', last_name='maine', phone='07048581078', password='jeffmaine'
class User(AbstractBaseUser, PermissionsMixin):
    userId = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

class Organisation(models.Model):
    orgId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)
    users = models.ManyToManyField(User, related_name='organisations', blank=True)

    def __str__(self):
        return self.name