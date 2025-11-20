from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
from User.forms import CustomRegistrationForm, EditProfileForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.utils import timezone
from events.models import Event, RSVP,Category
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.views.generic import TemplateView, UpdateView,DetailView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy


User = get_user_model()

# Create your views here.

def get_user_roles(request):
    user = request.user
    return {
        'is_admin': user.groups.filter(name="Admin").exists() if user.is_authenticated else False,
        'is_organizer': user.groups.filter(name="Organizer").exists() if user.is_authenticated else False,
        'is_participant': user.groups.filter(name="Participant").exists() if user.is_authenticated else False,
    }



def sign_up(request):
    
    if request.user.is_authenticated:
        return redirect('home')

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
    


class ProfileView(DetailView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'profile_user'
    pk_url_kwarg = 'id'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()  

        
        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['profile_image'] = getattr(user, 'profile_image', None)
        context['member_since'] = user.date_joined
        context['phone_number'] = user.phone_number
        context['last_login'] = user.last_login

        context['member_since_formatted'] = user.date_joined.strftime('%B %d, %Y')
        context['last_login_formatted'] = user.last_login.strftime('%B %d, %Y %H:%M') if user.last_login else 'Never'

        return context



class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'update_profile.html'
    context_object_name = 'form'

    def get_object(self, queryset=None):
       
        return self.request.user

    def form_valid(self, form):
       
        form.save()
        return redirect('profile', id=self.request.user.id)

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit Profile"
        return context



class ChangePassword(PasswordChangeView):
    template_name = 'password_change.html'
    form_class = CustomPasswordChangeForm
    @login_required
    def sign_out(request):
        if request.method == 'POST':
            logout(request)
            return redirect('login')
        

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'reset_password.html'
    success_url = reverse_lazy('login')
    html_email_template_name = 'reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'reset_password.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)