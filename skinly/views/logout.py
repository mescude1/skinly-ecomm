from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_view(request):
    """Handle user logout for both GET and POST requests"""
    # Only log out if user is actually authenticated
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
    return redirect('skinly:home')
