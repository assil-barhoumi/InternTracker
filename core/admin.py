from django.contrib import admin
from .models import InternshipOffer, Intern, InternshipApplication, Interview

@admin.register(InternshipOffer)
class InternshipOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'duration','requirements','start_date','end_date')

@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = ('user', 'cv')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    list_display = ('intern', 'internship_offer', 'status', 'applied_at')

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('get_intern', 'get_internship_offer', 'date_time', 'status','archived')

    def get_intern(self, obj):
        return obj.application.intern
    get_intern.short_description = 'Intern'

    def get_internship_offer(self, obj):
        return obj.application.internship_offer
    get_internship_offer.short_description = 'Internship Offer'