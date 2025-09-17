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
        "Color", blank=True, related_name="taste_profiles"
    )
    preferred_product_types = models.CharField(
        max_length=500, blank=True, help_text="Comma-separated product types"
    )
    preferred_finish_types = models.CharField(
        max_length=500, blank=True, help_text="Comma-separated finish types"
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
        "Brand", on_delete=models.CASCADE, related_name="taste_affinities"
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
        "Product", blank=True, related_name="wishlisted_by"
    )

    # marcas preferidas
    preferred_brands = models.ManyToManyField(
        "Brand", blank=True, related_name="preferred_by_users"
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
    
## Cart

class Cart(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="cart")
    # items relationship is handled by the CartItem model

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self) -> str:
        return f"Cart of {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name} in {self.cart}"

class Order(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    # products relationship is handled by the OrderItem model
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

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("order", "product")
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

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

class RecommendationEngine(models.Model):
    name = models.CharField(max_length=100, default="Main Engine")
    version = models.CharField(max_length=20, default="1.0")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recommendation Engine"
        verbose_name_plural = "Recommendation Engines"

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"

    def generate_recommendations(self, user, limit=10):
        """Generate product recommendations for a user based on their taste profile"""
        from django.db.models import Q, Avg
        
        if not user.taste_profile:
            return Product.objects.filter(stock_quantity__gt=0)[:limit]
        
        taste = user.taste_profile
        recommended_products = Product.objects.filter(stock_quantity__gt=0)
        
        # Filter by skin compatibility
        if user.skin_type:
            recommended_products = recommended_products.filter(
                Q(skin_type_compatibility__isnull=True) | 
                Q(skin_type_compatibility=user.skin_type)
            )
        
        # Filter by preferred product types
        if taste.preferred_product_types:
            product_types = taste.preferred_product_types.split(',')
            recommended_products = recommended_products.filter(
                product_type__in=product_types
            )
        
        # Filter by preferred colors
        if taste.preferred_colors.exists():
            recommended_products = recommended_products.filter(
                color__in=taste.preferred_colors.all()
            )
        
        # Filter by finish preferences
        if taste.preferred_finish_types:
            finish_types = taste.preferred_finish_types.split(',')
            recommended_products = recommended_products.filter(
                finish_type__in=finish_types
            )
        
        # Filter by price range
        if taste.price_range:
            recommended_products = recommended_products.filter(
                price__gte=taste.price_range.min_price,
                price__lte=taste.price_range.max_price
            )
        
        # Filter by preferred brands
        if user.preferred_brands.exists():
            recommended_products = recommended_products.filter(
                brand__in=user.preferred_brands.all()
            )
        
        return recommended_products.distinct()[:limit]

    def update_taste_profile(self, user, product, feedback):
        """Update user's taste profile based on product feedback"""
        if not user.taste_profile:
            user.taste_profile = TasteProfile.objects.create()
            user.save()
        
        taste = user.taste_profile
        
        if feedback.lower() in ['like', 'love', 'positive']:
            # Add product attributes to preferences
            if product.color and product.color not in taste.preferred_colors.all():
                taste.preferred_colors.add(product.color)
            
            # Add product type if not already in preferences
            current_types = taste.preferred_product_types.split(',') if taste.preferred_product_types else []
            if product.product_type and product.product_type not in current_types:
                current_types.append(product.product_type)
                taste.preferred_product_types = ','.join(current_types)
            
            # Add finish type if not already in preferences
            current_finishes = taste.preferred_finish_types.split(',') if taste.preferred_finish_types else []
            if product.finish_type and product.finish_type not in current_finishes:
                current_finishes.append(product.finish_type)
                taste.preferred_finish_types = ','.join(current_finishes)
            
            taste.save()
            
            # Increase brand affinity
            affinity, created = TasteBrandAffinity.objects.get_or_create(
                taste_profile=taste,
                brand=product.brand,
                defaults={'score': 0.1}
            )
            if not created:
                affinity.score = min(1.0, affinity.score + 0.1)
                affinity.save()

class SearchEngine(models.Model):
    name = models.CharField(max_length=100, default="Product Search")
    version = models.CharField(max_length=20, default="1.0")

    class Meta:
        verbose_name = "Search Engine"
        verbose_name_plural = "Search Engines"

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"

    def search(self, query, filters=None):
        """Search products by query and optional filters"""
        from django.db.models import Q
        
        products = Product.objects.filter(stock_quantity__gt=0)
        
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(product_type__icontains=query) |
                Q(color__name__icontains=query)
            )
        
        if filters:
            if 'brand' in filters:
                products = products.filter(brand__id__in=filters['brand'])
            
            if 'product_type' in filters:
                products = products.filter(product_type__in=filters['product_type'])
            
            if 'skin_type' in filters:
                products = products.filter(
                    Q(skin_type_compatibility__isnull=True) |
                    Q(skin_type_compatibility__in=filters['skin_type'])
                )
            
            if 'price_min' in filters:
                products = products.filter(price__gte=filters['price_min'])
            
            if 'price_max' in filters:
                products = products.filter(price__lte=filters['price_max'])
            
            if 'finish_type' in filters:
                products = products.filter(finish_type__in=filters['finish_type'])
        
        return products


# Newsletter
# ─────────────────────────────────────────
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

class InventoryManager(models.Model):
    name = models.CharField(max_length=100, default="Inventory System")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory Manager"
        verbose_name_plural = "Inventory Managers"

    def __str__(self) -> str:
        return self.name

    def update_stock(self, product_id, new_quantity):
        """Update stock quantity for a product"""
        try:
            product = Product.objects.get(id=product_id)
            product.stock_quantity = new_quantity
            product.save()
            return True
        except Product.DoesNotExist:
            return False

    def check_availability(self, product_id):
        """Check if product is available in stock"""
        try:
            product = Product.objects.get(id=product_id)
            return product.stock_quantity > 0
        except Product.DoesNotExist:
            return False

    def reduce_stock(self, product_id, quantity):
        """Reduce stock quantity (for orders)"""
        try:
            product = Product.objects.get(id=product_id)
            if product.stock_quantity >= quantity:
                product.stock_quantity -= quantity
                product.save()
                return True
            return False
        except Product.DoesNotExist:
            return False

    def get_low_stock_products(self, threshold=10):
        """Get products with low stock"""
        return Product.objects.filter(stock_quantity__lte=threshold)

