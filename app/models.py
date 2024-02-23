# models.py
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Enter Email')
        user = self.model(
            username=username,
            email=self.normalize_email(email)  # メールアドレスを正規化
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_absolute_url(self):
        return reverse_lazy('app:home')


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username  # または self.user.email


class Post(models.Model):
    GENRE_CHOICES = (
        ('漫画', '漫画'),
        ('アニメ', 'アニメ'),
        ('ゲーム', 'ゲーム'),
    )

    title = models.CharField(max_length=100)
    content = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='related_post', blank=True)
    genre = models.CharField(max_length=10, choices=GENRE_CHOICES)

    def __str__(self):
        return self.title

    class Meta:
       ordering = ["-created_at"]
