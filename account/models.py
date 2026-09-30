from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from main.models import Applicant


# Create your models here.
class User(AbstractUser):
    student = models.OneToOneField(Applicant, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Студент')
    slug = models.SlugField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
