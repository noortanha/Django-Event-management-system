from django.shortcuts import render, redirect,HttpResponse
from User.forms import CustomRegistrationForm
from django.contrib.auth import authenticate, login,logout

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.contrib import messages
from django.utils import timezone
from events.models import Event, RSVP,Category

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator


# Create your views here.

def get_user_roles(request):
    user = request.user
    return {
        'is_admin': user.groups.filter(name="Admin").exists() if user.is_authenticated else False,
        'is_organizer': user.groups.filter(name="Organizer").exists() if user.is_authenticated else False,
        'is_participant': user.groups.filter(name="Participant").exists() if user.is_authenticated else False,
    }

def sign_up(request):
    context = get_user_roles(request)
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomRegistrationForm()

    context['form'] = form
    return render(request, 'register.html', context)




def sign_in(request):
    context = get_user_roles(request)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.groups.filter(name='Admin').exists():
                    return redirect('admin-dashboard')
                elif user.groups.filter(name='Organizer').exists():
                    return redirect('organizer-dashboard')
                elif user.groups.filter(name='Participant').exists():
                    return redirect('participant-dashboard')
                else:
                    return redirect('home')
            else:
                messages.warning(request, "Please activate your account first.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', context)


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
 
    
def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('login')
        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')
    





