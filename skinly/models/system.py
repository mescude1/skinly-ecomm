"""
System related models (RecommendationEngine, SearchEngine, InventoryManager)
"""
from django.db import models


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
        from .product import Product
        from .user import TasteProfile, TasteBrandAffinity
        
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
        from .user import TasteProfile, TasteBrandAffinity
        
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
        from .product import Product
        
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
        from .product import Product
        
        try:
            product = Product.objects.get(id=product_id)
            product.stock_quantity = new_quantity
            product.save()
            return True
        except Product.DoesNotExist:
            return False

    def check_availability(self, product_id):
        """Check if product is available in stock"""
        from .product import Product
        
        try:
            product = Product.objects.get(id=product_id)
            return product.stock_quantity > 0
        except Product.DoesNotExist:
            return False

    def reduce_stock(self, product_id, quantity):
        """Reduce stock quantity (for orders)"""
        from .product import Product
        
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
        from .product import Product
        
        return Product.objects.filter(stock_quantity__lte=threshold)