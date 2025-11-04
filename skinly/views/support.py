import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from skinly.models import (
    NewsletterSubscriber, TasteProfile, Color, SkinTone, SkinType, 
    ProductType, FinishType, Review, Order, ShippingAddress, UserCouponAvailable
)


def privacy_policy_view(request):
    """Privacy policy page"""
    return render(request, 'skinly/privacy_policy.html')


def terms_of_service_view(request):
    """Terms of service page"""
    return render(request, 'skinly/terms_of_service.html')


@require_POST
def newsletter_subscribe(request):
    """Handle newsletter subscription"""

    logger = logging.getLogger(__name__)

    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip()

    logger.info(f"Newsletter subscription attempt for email: {email}")

    if not email:
        messages.error(request, 'Please provide a valid email address.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'name': name, 'is_active': True}
        )

        if created:
            messages.success(request,
                             'Thank you for subscribing to our newsletter! You\'ll receive the latest beauty tips and exclusive offers.')
            logger.info(f"New newsletter subscriber created: {email}")
        else:
            if subscriber.is_active:
                messages.info(request, 'You\'re already subscribed to our newsletter!')
                logger.info(f"Existing active subscriber tried to subscribe again: {email}")
            else:
                subscriber.is_active = True
                subscriber.save()
                messages.success(request, 'Welcome back! Your newsletter subscription has been reactivated.')
                logger.info(f"Reactivated newsletter subscriber: {email}")

    except Exception as e:
        logger.error(f"Newsletter subscription error for {email}: {str(e)}")
        messages.error(request, 'There was an error processing your subscription. Please try again.')

    # Return to the page where the form was submitted
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def profile_view(request):
    """User profile page"""
    if request.method == 'POST':
        # Handle profile update
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.skin_tone = request.POST.get('skin_tone', '')
        request.user.skin_type = request.POST.get('skin_type', '')
        request.user.save()
        
        # Update taste profile
        if not request.user.taste_profile:
            taste_profile = TasteProfile.objects.create()
            request.user.taste_profile = taste_profile
            request.user.save()
        else:
            taste_profile = request.user.taste_profile
        
        # Update taste profile preferences
        preferred_product_types = request.POST.getlist('preferred_product_types')
        preferred_finish_types = request.POST.getlist('preferred_finish_types')
        preferred_colors = request.POST.getlist('preferred_colors')
        
        taste_profile.preferred_product_types = ','.join(preferred_product_types)
        taste_profile.preferred_finish_types = ','.join(preferred_finish_types)
        taste_profile.save()
        
        # Update preferred colors
        taste_profile.preferred_colors.clear()
        if preferred_colors:
            preferred_colors_objects = Color.objects.filter(id__in=preferred_colors)
            taste_profile.preferred_colors.set(preferred_colors_objects)
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('skinly:profile')
    
    # GET request - display profile form
    user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')[:5]
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    available_coupons = UserCouponAvailable.objects.filter(
        user=request.user, 
        is_used=False,
        coupon__is_active=True
    ).select_related('coupon')
    
    # Get taste profile data
    taste_profile = request.user.taste_profile
    current_product_types = []
    current_finish_types = []
    if taste_profile:
        if taste_profile.preferred_product_types:
            current_product_types = taste_profile.preferred_product_types.split(',')
        if taste_profile.preferred_finish_types:
            current_finish_types = taste_profile.preferred_finish_types.split(',')
    
    context = {
        'skin_tones': SkinTone.choices,
        'skin_types': SkinType.choices,
        'product_types': ProductType.choices,
        'finish_types': FinishType.choices,
        'colors': Color.objects.all(),
        'user_reviews': user_reviews,
        'user_orders': user_orders,
        'shipping_addresses': shipping_addresses,
        'available_coupons': available_coupons,
        'current_product_types': current_product_types,
        'current_finish_types': current_finish_types,
        'taste_profile': taste_profile,
    }
    return render(request, 'skinly/profile.html', context)


def contact_view(request):
    """Contact page"""
    return render(request, 'skinly/contact.html')


def shipping_info_view(request):
    """Shipping information page"""
    return render(request, 'skinly/shipping_info.html')


def returns_view(request):
    """Returns policy page"""
    return render(request, 'skinly/returns.html')