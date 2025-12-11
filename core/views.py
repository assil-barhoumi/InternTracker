from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import InternshipOffer , Intern , InternshipApplication, Interview
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .forms import CVUploadForm, CustomUserCreationForm, UserEditForm
from django.utils import timezone
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Safe import for intern_required decorator
try:
    from .decorators import intern_required
except ImportError:
    # Fallback decorator that does nothing
    def intern_required(view_func):
        return view_func

# Custom Login View with reverse_lazy
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        # Check if the user is admin and trying to login through regular login page
        user = form.get_user()
        if user.is_staff or user.is_superuser:
            messages.error(self.request, "Admin users must use /admin/login to access the admin interface.")
            return redirect('login')
        
        return super().form_valid(form)
    
    def get_success_url(self):
        # For regular users, redirect to dashboard
        return reverse_lazy('dashboard')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Intern.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('offer_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return offer_list(request)

@intern_required
def dashboard(request):
    intern = get_object_or_404(Intern, user=request.user)
    applications = InternshipApplication.objects.filter(intern=intern).select_related('internship_offer').order_by('-applied_at')

    all_applications = InternshipApplication.objects.filter(intern=intern)
    pending_count = all_applications.filter(status='pending').count()
    approved_count = all_applications.filter(status='approved').count()
    refused_count = all_applications.filter(status='refused').count()

    current_hour = timezone.now().hour
    if 5 <= current_hour < 12:
        time_greeting = 'morning'
        time_icon = '☀️'
    elif 12 <= current_hour < 18:
        time_greeting = 'afternoon'
        time_icon = '🌤️'
    elif 18 <= current_hour < 22:
        time_greeting = 'evening'
        time_icon = '🌙'
    else:
        time_greeting = 'night'
        time_icon = '🌙'

    return render(request, 'intern/dashboard.html', {
        'intern': intern,
        'applications': applications,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'refused_count': refused_count,
        'time_greeting': time_greeting,
        'time_icon': time_icon,
    })


def offer_list(request):
    offers = InternshipOffer.objects.all()
    department = request.GET.get('department', '')
    duration = request.GET.get('duration', '')
    q = request.GET.get('q', '')

    if department:
        offers = offers.filter(department=department)
    if duration:
        offers = offers.filter(duration=duration)
    if q:
        offers = offers.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(requirements__icontains=q)
        )

    departments = InternshipOffer.objects.values_list('department', flat=True).distinct()
    all_offers = InternshipOffer.objects.all()
    durations = sorted(
        set(offer.duration for offer in all_offers if offer.duration),
        key=lambda x: int(x.split()[0]) if x.split() and x.split()[0].isdigit() else 0
    )
    paginator = Paginator(offers.order_by('-start_date'), 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'offers': page_obj.object_list,
        'departments': departments,
        'durations': durations,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'request': request,
        'selected_department': department,
        'selected_duration': duration,
        'search_query': q,
    }
    return render(request, "offers/offer_list.html", context)


@intern_required
def apply_offer(request, offer_id):
    offer = get_object_or_404(InternshipOffer, id=offer_id)
    intern, _ = Intern.objects.get_or_create(user=request.user)

    if not intern.cv:
        messages.warning(request, "Please upload your CV before applying to offers.")
        return redirect('upload_cv')

    if InternshipApplication.objects.filter(intern=intern, internship_offer=offer).exists():
        messages.info(request, "You have already applied to this offer.")
        return redirect('offer_list')

    try:
        InternshipApplication.objects.create(intern=intern, internship_offer=offer)
        messages.success(request, "Application submitted successfully!")
    except Exception as e:
        messages.error(request, f"Cannot apply: {e}")

    return redirect('offer_list')


@intern_required
def upload_cv(request):
    intern, _ = Intern.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CVUploadForm(
            request.POST, 
            request.FILES, 
            instance=intern
        )
        
        if form.is_valid():
            form.save()
            
            intern.updated_at = timezone.now()
            intern.save()
            messages.success(request, "Your CV has been uploaded successfully!")
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = CVUploadForm(instance=intern)
    
    return render(request, 'intern/upload_cv.html', {
        'form': form,
        'intern': intern  
    })

@intern_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was updated successfully!')
            return redirect('profile')
    else:
        form = UserEditForm(instance=request.user)
    
    return render(request, 'intern/edit_profile.html', {'form': form})

@intern_required
def profile(request):
    intern = get_object_or_404(Intern, user=request.user)
    return render(request, 'intern/profile.html', {'intern': intern})

@staff_member_required
def admin_dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count
    import json
    
    total_applications = InternshipApplication.objects.count()
    pending_applications = InternshipApplication.objects.filter(status='pending').count()
    
    total_interns = Intern.objects.count()
    active_interns = Intern.objects.filter(applications__status='approved').distinct().count()
    
    now = timezone.now()
    week_from_now = now + timedelta(days=7)
    upcoming_interviews = Interview.objects.filter(date_time__gt=now, date_time__lte=week_from_now).count()
    interviews_this_week = Interview.objects.filter(date_time__gte=now, date_time__lte=week_from_now).count()
    
    active_offers = InternshipOffer.objects.filter(is_archived=False).count()
    total_offers = InternshipOffer.objects.count()
    
    recent_applications = InternshipApplication.objects.select_related('intern__user', 'internship_offer').order_by('-applied_at')[:5]
    upcoming_interviews_list = Interview.objects.select_related('application__intern__user', 'application__internship_offer').filter(date_time__gt=now).order_by('date_time')[:5]
    
    department_data = InternshipApplication.objects.values('internship_offer__department').annotate(count=Count('id')).order_by('-count')
    department_labels = json.dumps([item['internship_offer__department'] or 'Unknown' for item in department_data])
    department_counts = json.dumps([item['count'] for item in department_data])
    
    offers_by_department = InternshipOffer.objects.values('department').annotate(count=Count('id')).order_by('-count')
    offers_department_labels = json.dumps([item['department'] or 'Unknown' for item in offers_by_department])
    offers_department_data = json.dumps([item['count'] for item in offers_by_department])
    
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    interviews_by_day = {}
    for i in range(30):
        day = start_of_month + timedelta(days=i)
        if day > now:
            break
        day_interviews = Interview.objects.filter(date_time__date=day.date()).count()
        interviews_by_day[day.strftime('%m/%d')] = day_interviews
    
    interview_month_labels = json.dumps(list(interviews_by_day.keys()))
    interview_month_data = json.dumps(list(interviews_by_day.values()))
    
    context = {
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'active_interns': active_interns,
        'total_interns': total_interns,
        'upcoming_interviews': upcoming_interviews,
        'interviews_this_week': interviews_this_week,
        'active_offers': active_offers,
        'total_offers': total_offers,
        'recent_applications': recent_applications,
        'upcoming_interviews_list': upcoming_interviews_list,
        'department_labels': department_labels,
        'department_data': department_counts,
        'offers_department_labels': offers_department_labels,
        'offers_department_data': offers_department_data,
        'interview_month_labels': interview_month_labels,
        'interview_month_data': interview_month_data,
    }
    return render(request, 'admin/index.html', context)

@staff_member_required
def admin_application_list(request):
    status_filter = (request.GET.get('status') or '').lower()
    department_filter = request.GET.get('department') or ''

    status_choices = dict(InternshipApplication.STATUS_CHOICES)
    queryset = InternshipApplication.objects.select_related('intern__user', 'internship_offer').order_by('-applied_at')

    if status_filter not in status_choices:
        status_filter = ''
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if department_filter:
        queryset = queryset.filter(internship_offer__department=department_filter)

    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')
        if application_id and action in {'approve', 'reject'}:
            application = get_object_or_404(InternshipApplication, pk=application_id)
            new_status = 'approved' if action == 'approve' else 'refused'
            if application.status == new_status:
                messages.info(request, "No status change was required for this application.")
            else:
                application.status = new_status
                application.save()
                messages.success(
                    request,
                    f"Application for {application.intern.user.get_full_name() or application.intern.user.username} "
                    f"marked as {application.get_status_display()}."
                )
        return redirect(request.get_full_path())

    departments = (
        InternshipOffer.objects.exclude(department__in=['', None])
        .values_list('department', flat=True)
        .order_by('department')
        .distinct()
    )

    page_obj = Paginator(queryset, 10).get_page(request.GET.get('page'))

    context = {
        'applications': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'status_choices': status_choices,
        'departments': departments,
        'current_status': status_filter,
        'current_department': department_filter,
    }
    return render(request, 'admin/applications_list.html', context)

@staff_member_required
def admin_interviews_list(request):
    status = request.GET.get('status', '')
    interviews = Interview.objects.select_related('application__intern__user', 'application__internship_offer').order_by('-date_time')
    if status:
        interviews = interviews.filter(status=status)
    return render(request, 'admin/interviews_list.html', {'interviews': interviews, 'current_status': status})

@staff_member_required
def admin_offers_list(request):
    archived = request.GET.get('archived')
    offers = InternshipOffer.objects.all().order_by('-start_date')
    if archived:
        offers = offers.filter(is_archived=True)
    else:
        offers = offers.filter(is_archived=False)
    return render(request, 'admin/offers_list.html', {'offers': offers, 'current_archived': archived})

@staff_member_required
def admin_interns_list(request):
    cv_status = request.GET.get('cv_status')
    interns = Intern.objects.select_related('user').order_by('-user__date_joined')
    if cv_status == 'has_cv':
        interns = interns.filter(cv__isnull=False)
    elif cv_status == 'no_cv':
        interns = interns.filter(cv__isnull=True)
    return render(request, 'admin/interns_list.html', {'interns': interns, 'current_cv': cv_status})