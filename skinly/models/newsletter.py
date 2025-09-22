"""
Newsletter related models
"""
from django.db import models


class NewsletterSubscriber(models.Model):
    """Newsletter subscription model"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # User preferences
    interests = models.ManyToManyField('Product', blank=True, related_name='newsletter_interested_users')
    
    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"


class NewsletterCampaign(models.Model):
    """Newsletter campaign model for tracking sent emails"""
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    recipients_count = models.PositiveIntegerField(default=0)
    
    # Featured products for this campaign
    featured_products = models.ManyToManyField('Product', blank=True, related_name='newsletter_campaigns')
    
    class Meta:
        verbose_name = "Newsletter Campaign"
        verbose_name_plural = "Newsletter Campaigns"
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.title} - {self.sent_at.strftime('%Y-%m-%d')}"