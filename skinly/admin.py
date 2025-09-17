from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User, PriceRange, TasteProfile, TasteBrandAffinity,
    Product, Brand, Color, Cart, CartItem, Order, OrderItem,
    Payment, PaymentMethod, Review, RecommendationEngine,
    SearchEngine, InventoryManager
)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Skin & Preferences", {
            "fields": ("skin_tone", "skin_type", "taste_profile", "wishlist", "preferred_brands")
        }),
    )
    list_display = ("username", "email", "skin_tone", "skin_type", "is_staff")
    search_fields = ("username", "email")
    filter_horizontal = ("wishlist", "preferred_brands")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "product_type", "price", "stock_quantity", "rating")
    list_filter = ("brand", "product_type", "finish_type", "skin_type_compatibility")
    search_fields = ("name", "brand__name")
    ordering = ("name",)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code")
    search_fields = ("name",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")
    list_filter = ("order__created_at",)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "product__name")

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user",)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")

@admin.register(TasteProfile)
class TasteProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "preferred_product_types", "preferred_finish_types")
    filter_horizontal = ("preferred_colors",)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "payment_method", "status", "payment_date")
    list_filter = ("status", "payment_date")

# Register remaining models
admin.site.register(PriceRange)
admin.site.register(TasteBrandAffinity)
admin.site.register(PaymentMethod)
admin.site.register(RecommendationEngine)
admin.site.register(SearchEngine)
admin.site.register(InventoryManager)
