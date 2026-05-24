from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from .forms import ProfileUpdateForm, UserLoginForm, UserRegisterForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, 'Login successful.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Invalid username or password. Please check your details.'
        )
        return super().form_invalid(form)


class RegisterView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard')

        messages.error(request, 'Please correct the errors below.')
        return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your profile.')
        return redirect('login')

    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            instance=profile,
            user=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')

        messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    return render(request, 'accounts/profile.html', {'form': form})