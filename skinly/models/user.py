"""
User and Profile related models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
from .choices import SkinTone, SkinType


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
    def update_with_feedback(self, product, feedback: str):
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