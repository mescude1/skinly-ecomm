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
