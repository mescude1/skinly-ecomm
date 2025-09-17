def privacy_policy_view(request):
    """Privacy policy page"""
    return render(request, 'skinly/privacy_policy.html')


def terms_of_service_view(request):
    """Terms of service page"""
    return render(request, 'skinly/terms_of_service.html')


@require_POST
def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    from .models import NewsletterSubscriber
    import logging

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