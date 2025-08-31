from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class InternshipOffer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=200)
    duration = models.CharField(max_length=100)
    requirements = models.TextField()

    def __str__(self):
        return self.title


class Intern(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cv = models.FileField(upload_to='cvs/')
   
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class InternshipApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ]

    intern = models.ForeignKey(Intern, on_delete=models.CASCADE, related_name='applications')
    internship_offer = models.ForeignKey(InternshipOffer, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('intern', 'internship_offer')
 
    def __str__(self):
        return f"{self.intern} - {self.internship_offer.title} ({self.status})"

    
class Interview(models.Model):
    INTERVIEW_TYPES = [
        ('zoom', 'Zoom'),
        ('in_person', 'In Person'),
    ]

    application = models.ForeignKey(InternshipApplication, on_delete=models.CASCADE, related_name='interviews', null=True, blank=True)
    date_time = models.DateTimeField()
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.application.intern.user.get_full_name()} - {self.application.internship_offer.title}"