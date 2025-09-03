from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import InternshipOffer , Intern , InternshipApplication
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import CVUploadForm
from django.utils import timezone
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            Intern.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('offer_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    return offer_list(request)  

@login_required
def dashboard(request):
    intern = get_object_or_404(Intern, user=request.user)
    apps = InternshipApplication.objects.filter(intern=intern).select_related('internship_offer').order_by('-applied_at')
    return render(request, 'intern/dashboard.html', {'intern': intern, 'applications': apps})


def offer_list(request):
    offers = InternshipOffer.objects.all()
    return render(request, "offers/offer_list.html", {"offers": offers})


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
