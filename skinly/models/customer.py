"""
Customer related models (Coupons, Shipping Addresses)
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class ShippingAddress(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="shipping_addresses")
    name = models.CharField(max_length=100, help_text="Address name/label (e.g., Home, Work)")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="USA")
    phone = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Shipping Address"
        verbose_name_plural = "Shipping Addresses"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            ShippingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited use")
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_valid(self):
        """Check if coupon is currently valid"""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )

    def get_discount_amount(self, order_total):
        """Calculate discount amount for given order total"""
        if not self.is_valid or order_total < self.minimum_order_amount:
            return Decimal('0.00')
        
        if self.discount_type == 'PERCENTAGE':
            return (order_total * self.discount_value / 100).quantize(Decimal('0.01'))
        else:  # FIXED
            return min(self.discount_value, order_total)


class UserCoupon(models.Model):
    """Track which coupons users have used"""
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="used_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="users_used")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="coupon_usage", null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "User Coupon Usage"
        verbose_name_plural = "User Coupon Usages"
        unique_together = ("user", "coupon", "order")

    def __str__(self):
        return f"{self.user} used {self.coupon.code}"


class UserCouponAvailable(models.Model):
    """Track which coupons are available to users"""
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="available_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="available_to_users")
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Available User Coupon"
        verbose_name_plural = "Available User Coupons"
        unique_together = ("user", "coupon")

    def __str__(self):
        status = "Used" if self.is_used else "Available"
        return f"{self.coupon.code} - {self.user} ({status})"