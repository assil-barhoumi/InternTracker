from django.contrib import admin
from .models import InternshipOffer, Intern, Interview

@admin.register(InternshipOffer)
class InternshipOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'duration')

@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = ('user', 'status')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('intern', 'internship_offer', 'date_time', 'completed')
