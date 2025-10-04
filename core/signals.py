from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import Intern, Interview


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

@receiver(post_save, sender=Interview)
def send_interview_email(sender, instance, created, **kwargs):
    if created and instance.status == 'scheduled' and instance.application:
        user = instance.application.intern.user
        if not user.email:
            return

        context = {
            'user': user,
            'offer': instance.application.internship_offer,
            'interview_date': instance.date_time.strftime("%A, %B %d, %Y"),
            'interview_time': instance.date_time.strftime("%I:%M %p"),
            'interview_type': instance.get_interview_type_display(),
            'zoom_link': instance.zoom_link,
            'location': instance.location,
        }

        subject = "Interview Scheduled"
        html_body = render_to_string('emails/interview_scheduled.html', context)

        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.content_subtype = "html"
        email.send(fail_silently=True)