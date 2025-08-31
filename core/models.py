from django.db import models
from django.contrib.auth.models import User

class InternshipOffer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=200)
    duration = models.CharField(max_length=100)
    requirements = models.TextField()

    def __str__(self):
        return self.title


class Intern(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approuved'),
        ('refused', 'Refused'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cv = models.FileField(upload_to='cvs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Interview(models.Model):
    INTERVIEW_TYPES = [
        ('zoom', 'Zoom'),
        ('in_person', 'In Person'),
    ]

    intern = models.ForeignKey(Intern, on_delete=models.CASCADE)
    internship_offer = models.ForeignKey(InternshipOffer, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.intern.user.get_full_name()} - {self.internship_offer.title}"