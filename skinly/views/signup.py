from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from skinly.forms import SignUpForm


def signup_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('skinly:home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Welcome to Skinly.')
            login(request, user)
            return redirect('skinly:home')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})
