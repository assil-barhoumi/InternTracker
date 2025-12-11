from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta


class InternshipOffer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=200)
    duration = models.CharField(max_length=100, help_text="e.g., '3 months', '6 months', '1 year'")
    requirements = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if self.start_date and self.duration:
            try:
                duration_parts = self.duration.lower().split()
                if len(duration_parts) >= 2:
                    amount = int(duration_parts[0])
                    unit = duration_parts[1]
                    
                    if 'month' in unit:
                        calculated_end_date = self.start_date + timedelta(days=amount*30)
                    elif 'year' in unit:
                        calculated_end_date = self.start_date + timedelta(days=amount*365)
                    else:
                        raise ValidationError("Duration must be in months or years")
                    
                    if self.end_date and self.end_date != calculated_end_date:
                        raise ValidationError(
                            f"End date must be {calculated_end_date} based on duration of {self.duration}"
                        )
                    
                    if not self.end_date:
                        self.end_date = calculated_end_date
                        
            except (ValueError, IndexError):
                raise ValidationError("Invalid duration format. Use format like '3 months' or '1 year'")
        
        if self.start_date and self.start_date < date.today():
            raise ValidationError("start date cannot be in the past")

    def save(self, *args, **kwargs):
        if self.start_date and self.duration and not self.end_date:
            try:
                duration_parts = self.duration.lower().split()
                if len(duration_parts) >= 2:
                    amount = int(duration_parts[0])
                    unit = duration_parts[1]
                    
                    if 'month' in unit:
                        self.end_date = self.start_date + timedelta(days=amount*30)
                    elif 'year' in unit:
                        self.end_date = self.start_date + timedelta(days=amount*365)
            except (ValueError, IndexError):
                pass
        
        super().save(*args, **kwargs)

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
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    INTERVIEW_TYPES = [
        ('zoom', 'Zoom'),
        ('in_person', 'In Person'),
    ]
    
    application = models.OneToOneField(InternshipApplication, on_delete=models.CASCADE, related_name='interview', null=True, blank=True)
    date_time = models.DateTimeField()
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    zoom_link = models.URLField(blank=True, help_text="Required for Zoom interviews")
    location = models.TextField(blank=True, null=True, help_text="Required for in-person interviews")
    notes = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True, help_text="Interview feedback and evaluation")
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.application:
            return f"{self.application.intern} - {self.application.internship_offer.title} - {self.date_time}"
        return f"Interview #{self.id} - {self.date_time}"
    
    def clean(self):
        if self.date_time and self.date_time < timezone.now() and self.status not in ['completed', 'cancelled', 'no_show']:
            raise ValidationError("Cannot schedule an interview in the past unless it's marked as completed, cancelled, or no-show.")
            
        if self.interview_type == "zoom":
            if not self.zoom_link and self.status != 'cancelled':
                raise ValidationError("Zoom link is required for Zoom interviews.")
            if self.location:
                raise ValidationError("Location must be empty for Zoom interviews.")
        
        if self.interview_type == "in_person":
            if not self.location and self.status != 'cancelled':
                raise ValidationError("Location is required for in-person interviews.")
            if self.zoom_link:
                raise ValidationError("Zoom link must be empty for in-person interviews.")
                
        if self.status == 'completed' and not self.feedback:
            self.feedback = 'Completed as scheduled.'
