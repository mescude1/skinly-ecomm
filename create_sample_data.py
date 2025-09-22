#!/usr/bin/env python
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skinly_core.settings')
django.setup()

from skinly.models import *

# Create Colors
colors_data = [
    ("Ruby Red", "#DC143C"),
    ("Golden Glow", "#FFD700"),
    ("Rose Pink", "#FF69B4"),
    ("Nude Beige", "#F5DEB3"),
    ("Coral Sunset", "#FF7F50"),
    ("Berry Wine", "#8B0000"),
    ("Champagne", "#F7E7CE"),
    ("Classic Black", "#000000"),
    ("Chocolate Brown", "#D2691E"),
    ("Peach Blush", "#FFCBA4"),
]

for name, hex_code in colors_data:
    Color.objects.get_or_create(name=name, defaults={'hex_code': hex_code})

# Create Brands
brands_data = [
    ("Fenty Beauty", "Beauty for all skin tones by Rihanna"),
    ("Rare Beauty", "Mental health focused beauty by Selena Gomez"),
    ("Charlotte Tilbury", "Luxury makeup with Hollywood glamour"),
    ("Glossier", "Beauty inspired by real life"),
    ("NARS", "French cosmetics with bold attitude"),
    ("MAC Cosmetics", "Professional makeup for all"),
    ("Urban Decay", "Beauty with an edge"),
    ("Too Faced", "Fun and feminine cosmetics"),
]

for name, description in brands_data:
    Brand.objects.get_or_create(name=name, defaults={'description': description})

# Create Price Ranges
price_ranges = [
    (Decimal('10.00'), Decimal('25.00')),
    (Decimal('25.00'), Decimal('50.00')),
    (Decimal('50.00'), Decimal('100.00')),
    (Decimal('100.00'), Decimal('200.00')),
]

for min_price, max_price in price_ranges:
    PriceRange.objects.get_or_create(
        min_price=min_price,
        max_price=max_price
    )

# Get created objects
brands = list(Brand.objects.all())
colors = list(Color.objects.all())

# Create Products
products_data = [
    # Foundations
    ("Pro Filt'r Soft Matte Foundation", brands[0], ProductType.FOUNDATION, FinishType.MATTE, colors[3], Decimal('36.00'), SkinType.OILY, 50),
    ("Rare Beauty Foundation", brands[1], ProductType.FOUNDATION, FinishType.DEWY, colors[3], Decimal('29.00'), SkinType.DRY, 45),
    ("Magic Foundation", brands[2], ProductType.FOUNDATION, FinishType.SATIN, colors[6], Decimal('44.00'), SkinType.NORMAL, 30),
    
    # Lipsticks
    ("Stunna Lip Paint", brands[0], ProductType.LIPSTICK, FinishType.MATTE, colors[0], Decimal('24.00'), None, 75),
    ("Soft Pinch Lipstick", brands[1], ProductType.LIPSTICK, FinishType.SATIN, colors[2], Decimal('20.00'), None, 60),
    ("Matte Revolution", brands[2], ProductType.LIPSTICK, FinishType.MATTE, colors[5], Decimal('34.00'), None, 40),
    ("Audacious Lipstick", brands[4], ProductType.LIPSTICK, FinishType.GLOSSY, colors[4], Decimal('38.00'), None, 35),
    
    # Mascaras
    ("Full Frontal Mascara", brands[0], ProductType.MASCARA, FinishType.MATTE, colors[7], Decimal('24.00'), None, 80),
    ("Perfect Strokes Mascara", brands[1], ProductType.MASCARA, FinishType.MATTE, colors[7], Decimal('19.00'), None, 70),
    ("Pillow Talk Push Up Lashes", brands[2], ProductType.MASCARA, FinishType.MATTE, colors[7], Decimal('29.00'), None, 55),
    
    # Blushes
    ("Cheeks Out Blush", brands[0], ProductType.BLUSH, FinishType.SATIN, colors[2], Decimal('20.00'), None, 65),
    ("Soft Pinch Blush", brands[1], ProductType.BLUSH, FinishType.DEWY, colors[9], Decimal('23.00'), None, 50),
    ("Cheek to Chic", brands[2], ProductType.BLUSH, FinishType.SHIMMER, colors[4], Decimal('40.00'), None, 25),
    
    # Eyeshadows
    ("Snap Shadows", brands[0], ProductType.EYESHADOW, FinishType.SHIMMER, colors[6], Decimal('25.00'), None, 40),
    ("Perfect Strokes Eyeshadow", brands[1], ProductType.EYESHADOW, FinishType.MATTE, colors[8], Decimal('22.00'), None, 35),
    ("Eyes to Mesmerize", brands[2], ProductType.EYESHADOW, FinishType.SHIMMER, colors[1], Decimal('32.00'), None, 30),
]

for name, brand, product_type, finish_type, color, price, skin_compat, stock in products_data:
    Product.objects.get_or_create(
        name=name,
        defaults={
            'brand': brand,
            'product_type': product_type,
            'finish_type': finish_type,
            'color': color,
            'price': price,
            'skin_type_compatibility': skin_compat,
            'stock_quantity': stock,
            'rating': 4.5  # Default good rating
        }
    )

# Create Recommendation Engine
RecommendationEngine.objects.get_or_create(
    name="Skinly AI Recommender",
    defaults={'version': '1.0'}
)

# Create Search Engine
SearchEngine.objects.get_or_create(
    name="Skinly Product Search",
    defaults={'version': '1.0'}
)

# Create Inventory Manager
InventoryManager.objects.get_or_create(
    name="Skinly Inventory System",
    defaults={}
)

print("✅ Sample data created successfully!")
print(f"📊 Created:")
print(f"   - {Color.objects.count()} colors")
print(f"   - {Brand.objects.count()} brands") 
print(f"   - {Product.objects.count()} products")
print(f"   - {PriceRange.objects.count()} price ranges")
print()
print("🚀 Your Skinly application is ready!")
print("🌐 Visit: http://127.0.0.1:8000/")
print("🔧 Admin: http://127.0.0.1:8000/admin/")
print("👤 Admin login: admin / admin123")