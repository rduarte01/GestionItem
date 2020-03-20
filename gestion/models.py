from django.db import models

# Create your models here.

#class User(models.Model):
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from django.db.models.signals import post_save

@receiver(pre_save, sender=User)
def set_new_user_inactive(sender, instance, **kwargs):
    """Lo que hace es setear a todos los usuarios recien registrados, por defecto
    en estado inactivo, a excepcion de los que son creados como superusuarios"""
    if instance._state.adding is True and User.is_superuser is False:
        print("Creating Inactive User")
        instance.is_active = False
    else:
        print("Updating User Record")



"""class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()"""