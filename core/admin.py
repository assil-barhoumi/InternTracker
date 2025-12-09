from django.contrib import admin
from .models import InternshipOffer, Intern, InternshipApplication, Interview

from django.utils.html import format_html
from django.urls import reverse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

@admin.register(InternshipOffer)
class InternshipOfferAdmin(admin.ModelAdmin):
    change_form_template = "admin/core/internshipoffer/change_form.html"
    list_display = ('title', 'department', 'start_date', 'end_date', 'is_archived', 'application_count', 'view_applications_link')
    list_filter = ('department', 'is_archived', 'start_date', 'end_date')
    actions = ['archive_selected', 'unarchive_selected']
    date_hierarchy = 'start_date'
    fieldsets = [
        (None, {
            'fields': ('title', 'description', 'department', 'duration', 'requirements', 'start_date', 'end_date')
        }),
    ]
    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'

    def view_applications_link(self, obj):
        url = f"{reverse('admin:core_internshipapplication_changelist')}?internship_offer__id__exact={obj.id}"
        return format_html('<a href="{}">View Applications</a>', url)
    view_applications_link.short_description = 'Applications'

    def archive_selected(self, request, queryset):
        updated = queryset.update(is_archived=True)
        self.message_user(request, f"{updated} internship offer(s) archived successfully.")
    archive_selected.short_description = "Archive selected offers"

    def unarchive_selected(self, request, queryset):
        updated = queryset.update(is_archived=False)
        self.message_user(request, f"{updated} internship offer(s) unarchived successfully.")
    unarchive_selected.short_description = "Unarchive selected offers"

    def response_change(self, request, obj):
        if '_save' in request.POST:
            self.message_user(request, "Offer saved successfully.", messages.SUCCESS)
            return redirect('admin_offers_list')
        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if '_save' in request.POST:
            self.message_user(request, "Offer added successfully.", messages.SUCCESS)
            return redirect('admin_offers_list')
        return super().response_add(request, obj, post_url_continue)

@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'cv_link', 'application_count')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('user__is_active',)
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'

    def cv_link(self, obj):
        if obj.cv:
            return format_html('<a href="{0}" target="_blank">View CV</a>', obj.cv.url)
        return "No CV"
    cv_link.short_description = 'CV'

    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'

@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    change_form_template = "admin/applications/detail.html"
    list_display = ('intern', 'internship_offer', 'status', 'applied_at', 'interview_status')
    list_filter = ('status', 'internship_offer__department', 'applied_at')
    search_fields = ('intern__user__username', 'internship_offer__title', 'intern__user__email')
    list_editable = ('status',)
    actions = ['approve_applications', 'reject_applications', 'schedule_interview']
    date_hierarchy = 'applied_at'

    def changelist_view(self, request, extra_context=None):
        return redirect('admin_application_list')

    def has_change_permission(self, request, obj=None):
        # allow viewing detail page (fields remain readonly)
        return True
        
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [f.name for f in self.model._meta.fields if f.name != 'status']
        return []
        
    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        application = get_object_or_404(
            InternshipApplication.objects.select_related('intern__user', 'internship_offer'),
            pk=object_id
        )
        interviews = application.interviews.order_by('-date_time')

        extra_context = extra_context or {}
        extra_context.update({
            'application_obj': application,
            'interviews': interviews,
        })
        return super().change_view(request, object_id, form_url, extra_context)

    def interview_status(self, obj):
        interview = obj.interviews.first()
        if interview:
            return f"{interview.get_interview_type_display()} - {'Completed' if interview.status == 'completed' else 'Pending'}"
        return "No Interview"
    interview_status.short_description = 'Interview Status'

    def approve_applications(self, request, queryset):
        updated = 0
        for application in queryset:
            if application.status != 'approved':
                application.status = 'approved'
                application.save()

                if application.intern.user.email:
                    context = {
                        'user': application.intern.user,
                        'offer': application.internship_offer,
                    }

                    subject = f"Application Approved - {application.internship_offer.title}"
                    html_body = render_to_string('emails/application_approved.html', context)

                    email = EmailMessage(
                        subject=subject,
                        body=html_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[application.intern.user.email]
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=True)

                updated += 1

        self.message_user(request, f"{updated} application(s) approved and notified successfully.")
    approve_applications.short_description = "Approve selected applications"

    def reject_applications(self, request, queryset):
        updated = 0
        for application in queryset:
            if application.status != 'refused':
                application.status = 'refused'
                application.save()

                if application.intern.user.email:
                    context = {
                        'user': application.intern.user,
                        'offer': application.internship_offer,
                    }

                    subject = f"Application Not Selected - {application.internship_offer.title}"
                    html_body = render_to_string('emails/application_rejected.html', context)

                    email = EmailMessage(
                        subject=subject,
                        body=html_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[application.intern.user.email]
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=True)

                updated += 1

        self.message_user(request, f"{updated} application(s) rejected and notified successfully.")
    reject_applications.short_description = "Reject selected applications"

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    change_form_template = "admin/core/interview/change_form.html"
    list_display = ('get_intern', 'get_internship_offer', 'date_time', 'status', 'archived', 'time_until')
    list_filter = ('status', 'interview_type', 'archived', 'date_time')
    search_fields = ('application__intern__user__username', 'application__internship_offer__title')
    list_editable = ('status', 'archived')
    date_hierarchy = 'date_time'
    actions = ['mark_in_progress', 'mark_completed', 'mark_cancelled', 'mark_no_show', 'toggle_archived']
    fieldsets = [
        (None, {
            'fields': ('application', 'date_time', 'interview_type', 'status', 'zoom_link', 'location', 'notes', 'feedback')
        }),
    ]
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

    
    def response_change(self, request, obj):
         if '_save' in request.POST:
                 self.message_user(request, "Interview saved successfully.", messages.SUCCESS)
                 return redirect('admin_interviews_list')
         return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if '_save' in request.POST:
             self.message_user(request, "Interview saved successfully.", messages.SUCCESS)   
             return redirect('admin_interviews_list')
        return super().response_add(request, obj, post_url_continue)