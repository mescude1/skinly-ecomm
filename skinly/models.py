# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

# ─────────────────────────────────────────
# Enum choices
# ─────────────────────────────────────────
class SkinTone(models.TextChoices):
    FAIR = "FAIR", "Fair"
    LIGHT = "LIGHT", "Light"
    MEDIUM = "MEDIUM", "Medium"
    TAN = "TAN", "Tan"
    DEEP = "DEEP", "Deep"


class SkinType(models.TextChoices):
    OILY = "OILY", "Oily"
    DRY = "DRY", "Dry"
    COMBINATION = "COMBINATION", "Combination"
    SENSITIVE = "SENSITIVE", "Sensitive"
    NORMAL = "NORMAL", "Normal"

class ProductType(models.TextChoices):
    FOUNDATION = "FOUNDATION", "Foundation"
    CONCEALER = "CONCEALER", "Concealer"
    POWDER = "POWDER", "Powder"
    BLUSH = "BLUSH", "Blush"
    EYESHADOW = "EYESHADOW", "Eyeshadow"
    LIPSTICK = "LIPSTICK", "Lipstick"
    MASCARA = "MASCARA", "Mascara"
    EYELINER = "EYELINER", "Eyeliner"
    SKINCARE = "SKINCARE", "Skincare"
    OTHER = "OTHER", "Other"

class FinishType(models.TextChoices):
    MATTE = "MATTE", "Matte"
    DEWY = "DEWY", "Dewy"
    SATIN = "SATIN", "Satin"
    GLOSSY = "GLOSSY", "Glossy"
    SHIMMER = "SHIMMER", "Shimmer"

class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SHIPPED = "SHIPPED", "Shipped"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELED = "CANCELED", "Canceled"

class PaymentMethodType(models.TextChoices):
    CREDIT_CARD = "CREDIT_CARD", "Credit Card"
    DEBIT_CARD = "DEBIT_CARD", "Debit Card"
    PAYPAL = "PAYPAL", "PayPal"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY", "Cash on Delivery"

class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"

class PriceRange:
    min_price: Decimal
    max_price: Decimal


# ─────────────────────────────────────────
# Price range para el TasteProfile
# ─────────────────────────────────────────
class PriceRange(models.Model):
    min_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    max_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    class Meta:
        verbose_name = "Price range"
        verbose_name_plural = "Price ranges"

    def __str__(self) -> str:
        return f"{self.min_price} – {self.max_price}"


# ─────────────────────────────────────────
# OJO: Usamos referencias en string a modelos de otras apps
# 'catalog.Product', 'catalog.Brand', 'catalog.Color',
# 'catalog.ProductType', 'catalog.FinishType'
# ─────────────────────────────────────────

class TasteProfile(models.Model):
    # muchos-a-muchos con entidades del catálogo
    preferred_colors = models.ManyToManyField(
        "catalog.Color", blank=True, related_name="taste_profiles"
    )
    product_types = models.ManyToManyField(
        "catalog.ProductType", blank=True, related_name="taste_profiles"
    )
    finish_preferences = models.ManyToManyField(
        "catalog.FinishType", blank=True, related_name="taste_profiles"
    )

    # afinidad por marca (map<Brand,float>) mediante tabla intermedia
    price_range = models.OneToOneField(
        PriceRange, on_delete=models.CASCADE, null=True, blank=True, related_name="taste_profile"
    )

    class Meta:
        verbose_name = "Taste profile"
        verbose_name_plural = "Taste profiles"

    def __str__(self) -> str:
        return f"TasteProfile #{self.pk}"

    # placeholder para futura lógica de feedback
    def update_with_feedback(self, product: "catalog.Product", feedback: str):
        """
        Actualiza preferencias en base a feedback del usuario sobre un producto.
        Implementación básica (a completar cuando tengamos el motor de recomendación):
        - Podrías incrementar afinidad de la marca,
        - anexar product_type/finish/color si no estaban,
        - ajustar price_range observado.
        """
        # TODO: implementar cuando tengamos reglas/engine claro.
        pass


class TasteBrandAffinity(models.Model):
    taste_profile = models.ForeignKey(
        TasteProfile, on_delete=models.CASCADE, related_name="brand_affinities"
    )
    brand = models.ForeignKey(
        "catalog.Brand", on_delete=models.CASCADE, related_name="taste_affinities"
    )
    score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("taste_profile", "brand")
        verbose_name = "Brand affinity"
        verbose_name_plural = "Brand affinities"

    def __str__(self) -> str:
        return f"{self.taste_profile_id} · {self.brand_id} → {self.score}"


# ─────────────────────────────────────────
# Usuario personalizado
# ─────────────────────────────────────────
class User(AbstractUser):
    """
    Custom User que mantiene compatibilidad con Django admin/auth.
    username sigue existiendo; email único es recomendable.
    """
    email = models.EmailField(unique=True)

    skin_tone = models.CharField(
        max_length=16, choices=SkinTone.choices, null=True, blank=True
    )
    skin_type = models.CharField(
        max_length=16, choices=SkinType.choices, null=True, blank=True
    )

    taste_profile = models.OneToOneField(
        TasteProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="user"
    )

    # wishlist de productos
    wishlist = models.ManyToManyField(
        "catalog.Product", blank=True, related_name="wishlisted_by"
    )

    # marcas preferidas
    preferred_brands = models.ManyToManyField(
        "catalog.Brand", blank=True, related_name="preferred_by_users"
    )

    # NOTA: order_history no se define aquí; vendrá como relación inversa
    # desde Order.user (p.ej. 'orders').

    REQUIRED_FIELDS = ["email"]  # para createsuperuser

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.get_full_name() or self.username

## PRODUCT

class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey("catalog.Brand", on_delete=models.CASCADE, related_name="products")
    product_type = models.ForeignKey("catalog.ProductType", on_delete=models.CASCADE, related_name="products")
    finish_type = models.ForeignKey("catalog.FinishType", on_delete=models.CASCADE, related_name="products")
    color = models.ForeignKey("catalog.Color", on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    skin_type_compatibility = models.ForeignKey(
        "catalog.SkinType", on_delete=models.SET_NULL, null=True, blank=True, related_name="compatible_products"
    )
    stock_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    products = models.ManyToManyField("catalog.Product", through=Product, related_name="brands")


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
    
## Cart

class Cart(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="cart")
    items = models.ManyToManyField("catalog.Product", through="CartItem", related_name="carts")

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self) -> str:
        return f"Cart of {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name} in {self.cart}"

class Order(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField("catalog.Product", through="OrderItem", related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        return f"Order #{self.id} by {self.user}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed")
    ], default="PENDING")

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self) -> str:
        return f"Payment for Order #{self.order.id} - {self.status}"

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"

    def __str__(self) -> str:
        return self.name

class Review(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MinValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self) -> str:
        return f"Review by {self.user} for {self.product} - {self.rating} stars"

