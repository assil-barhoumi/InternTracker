from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Intern

@receiver(post_save, sender=User)
def create_intern_profile(sender, instance, created, **kwargs):
    if created and not instance.is_staff and not instance.is_superuser:
        Intern.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_intern_profile(sender, instance, **kwargs):
    if not instance.is_staff and not instance.is_superuser:
        try:
            instance.intern.save()
        except Intern.DoesNotExist:
             Intern.objects.create(user=instance)
