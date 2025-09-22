"""
Product related models
"""
from django.db import models
from django.core.validators import MinValueValidator
from .choices import ProductType, FinishType, SkinType


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    # products relationship is handled by the Product model's brand ForeignKey

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self) -> str:
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hex_code = models.CharField(max_length=7, unique=True)  # e.g., #FFFFFF

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colors"

    def __str__(self) -> str:
        return f"{self.name} ({self.hex_code})"


class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey("Brand", on_delete=models.CASCADE, related_name="products")
    product_type = models.CharField(max_length=20, choices=ProductType.choices)
    finish_type = models.CharField(max_length=20, choices=FinishType.choices)
    color = models.ForeignKey("Color", on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    skin_type_compatibility = models.CharField(
        max_length=16, choices=SkinType.choices, null=True, blank=True
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MinValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self) -> str:
        return f"Review by {self.user} for {self.product} - {self.rating} stars"