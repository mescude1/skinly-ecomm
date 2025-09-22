#!/usr/bin/env python
"""
Newsletter sending script for Skinly.
Run this weekly to send newsletters to all active subscribers.

Usage:
    python send_newsletter.py
"""

import os
import django
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skinly_core.settings')
django.setup()

from skinly.models import NewsletterSubscriber, NewsletterCampaign, Product
from datetime import datetime


def create_weekly_newsletter():
    """Create and send weekly newsletter"""
    
    # Get active subscribers
    subscribers = NewsletterSubscriber.objects.filter(is_active=True)
    
    if not subscribers.exists():
        print("No active subscribers found.")
        return
    
    # Get featured products for this week (newest products)
    featured_products = Product.objects.filter(stock_quantity__gt=0).order_by('-id')[:4]
    
    # Create campaign
    campaign = NewsletterCampaign.objects.create(
        title="Weekly Beauty Essentials",
        subject=f"✨ Your Weekly Beauty Fix - {datetime.now().strftime('%B %d, %Y')}",
        content="Discover this week's must-have beauty products and get exclusive tips from our beauty experts.",
        recipients_count=subscribers.count()
    )
    
    # Add featured products to campaign
    campaign.featured_products.set(featured_products)
    
    # Render email template
    html_content = render_to_string('emails/newsletter.html', {
        'campaign': campaign,
        'featured_products': featured_products
    })
    
    # Send emails
    sent_count = 0
    failed_count = 0
    
    for subscriber in subscribers:
        try:
            # Create email
            email = EmailMultiAlternatives(
                subject=campaign.subject,
                body=f"Hello {subscriber.name or 'Beauty Lover'},\n\n{campaign.content}\n\nView this email in your browser: https://skinly.co/newsletter/\n\nBest regards,\nThe Skinly Team",
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'hello@skinly.co',
                to=[subscriber.email],
                headers={'List-Unsubscribe': '<https://skinly.co/newsletter/unsubscribe/>'}
            )
            
            # Attach HTML content
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            sent_count += 1
            print(f"✓ Sent to {subscriber.email}")
            
        except Exception as e:
            failed_count += 1
            print(f"✗ Failed to send to {subscriber.email}: {str(e)}")
    
    # Update campaign stats
    campaign.recipients_count = sent_count
    campaign.save()
    
    print(f"\n📊 Newsletter Summary:")
    print(f"   - Campaign: {campaign.title}")
    print(f"   - Total subscribers: {subscribers.count()}")
    print(f"   - Successfully sent: {sent_count}")
    print(f"   - Failed: {failed_count}")
    print(f"   - Featured products: {featured_products.count()}")
    print(f"\n🎉 Newsletter campaign completed!")


if __name__ == "__main__":
    print("🚀 Starting weekly newsletter campaign...")
    create_weekly_newsletter()