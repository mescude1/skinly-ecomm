# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, PriceRange, TasteProfile, TasteBrandAffinity

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Skin & Preferences", {
            "fields": ("skin_tone", "skin_type", "taste_profile", "wishlist", "preferred_brands")
        }),
    )
    list_display = ("username", "email", "skin_tone", "skin_type", "is_staff")
    search_fields = ("username", "email")

admin.site.register(PriceRange)
admin.site.register(TasteProfile)
admin.site.register(TasteBrandAffinity)
