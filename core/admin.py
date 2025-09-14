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
    list_display = ('intern', 'internship_offer', 'status', 'applied_at', 'interview_status')
    list_filter = ('status', 'internship_offer__department', 'applied_at')
    search_fields = ('intern__user__username', 'internship_offer__title', 'intern__user__email')
    list_editable = ('status',)
    actions = ['approve_applications', 'reject_applications', 'schedule_interview']
    date_hierarchy = 'applied_at'

    def has_change_permission(self, request, obj=None):
        return False
        
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [f.name for f in self.model._meta.fields if f.name != 'status']
        return []
        
    def has_delete_permission(self, request, obj=None):
        return False

    def interview_status(self, obj):
        interview = obj.interviews.first()
        if interview:
            return f"{interview.get_interview_type_display()} - {'Completed' if interview.status == 'completed' else 'Pending'}"
        return "No Interview"
    interview_status.short_description = 'Interview Status'

    def approve_applications(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} application(s) approved successfully.")
    approve_applications.short_description = "Approve selected applications"

    def reject_applications(self, request, queryset):
        updated = queryset.update(status='refused')
        self.message_user(request, f"{updated} application(s) rejected.")
    reject_applications.short_description = "Reject selected applications"

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('get_intern', 'get_internship_offer', 'date_time', 'status', 'archived', 'time_until')
    list_filter = ('status', 'interview_type', 'archived', 'date_time')
    search_fields = ('application__intern__user__username', 'application__internship_offer__title')
    list_editable = ('status', 'archived')
    date_hierarchy = 'date_time'
    actions = ['mark_in_progress', 'mark_completed', 'mark_cancelled', 'mark_no_show', 'toggle_archived']

    def get_intern(self, obj):
        return obj.application.intern.user.get_full_name() or obj.application.intern.user.username
    get_intern.short_description = 'Intern'
    get_intern.admin_order_field = 'application__intern__user__first_name'

    def get_internship_offer(self, obj):
        return obj.application.internship_offer.title
    get_internship_offer.short_description = 'Internship Offer'
    get_internship_offer.admin_order_field = 'application__internship_offer__title'

    def time_until(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if obj.date_time > now and obj.status == 'scheduled':
            delta = obj.date_time - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes = remainder // 60
            return f"In {days}d {hours}h {minutes}m"
        return obj.get_status_display()
    time_until.short_description = 'Status'

    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f"{updated} interview(s) marked as In Progress.")
    mark_in_progress.short_description = "Mark selected as In Progress"

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} interview(s) marked as Completed.")
    mark_completed.short_description = "Mark selected as Completed"

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} interview(s) marked as Cancelled.")
    mark_cancelled.short_description = "Mark selected as Cancelled"

    def mark_no_show(self, request, queryset):
        updated = queryset.update(status='no_show')
        self.message_user(request, f"{updated} interview(s) marked as No Show.")
    mark_no_show.short_description = "Mark selected as No Show"

    def toggle_archived(self, request, queryset):
        for obj in queryset:
            obj.archived = not obj.archived
            obj.save()
        self.message_user(request, f"Toggled archive status for {queryset.count()} interview(s).")
    toggle_archived.short_description = "Toggle archive status"