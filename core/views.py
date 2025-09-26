from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import InternshipOffer , Intern , InternshipApplication
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import CVUploadForm, CustomUserCreationForm, UserEditForm
from django.utils import timezone
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Q
    
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

@login_required
def dashboard(request):
    intern = get_object_or_404(Intern, user=request.user)
    applications = InternshipApplication.objects.filter(intern=intern).select_related('internship_offer').order_by('-applied_at')
    return render(request, 'intern/dashboard.html', {'intern': intern, 'applications': applications})


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


@login_required
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


@login_required
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

@login_required
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

@login_required
def profile(request):
    intern = get_object_or_404(Intern, user=request.user)
    return render(request, 'intern/profile.html', {'intern': intern})