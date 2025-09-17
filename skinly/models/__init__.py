"""
Models package for Skinly application
"""

# Import choices
from .choices import (
    SkinTone,
    SkinType,
    ProductType,
    FinishType,
    OrderStatus,
    PaymentMethodType,
)

# Import user and profile models
from .user import (
    PriceRange,
    TasteProfile,
    TasteBrandAffinity,
    User,
)

# Import product models
from .product import (
    Brand,
    Color,
    Product,
    Review,
)

# Import order and cart models
from .order import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    PaymentMethod,
)

# Import system models
from .system import (
    RecommendationEngine,
    SearchEngine,
    InventoryManager,
)

# Import newsletter models
from .newsletter import (
    NewsletterSubscriber,
    NewsletterCampaign,
)

# Make all models available when importing from models
__all__ = [
    # Choices
    'SkinTone',
    'SkinType', 
    'ProductType',
    'FinishType',
    'OrderStatus',
    'PaymentMethodType',
    
    # User and Profile
    'PriceRange',
    'TasteProfile',
    'TasteBrandAffinity',
    'User',
    
    # Product
    'Brand',
    'Color',
    'Product',
    'Review',
    
    # Order and Cart
    'Cart',
    'CartItem',
    'Order',
    'OrderItem',
    'Payment',
    'PaymentMethod',
    
    # System
    'RecommendationEngine',
    'SearchEngine',
    'InventoryManager',
    
    # Newsletter
    'NewsletterSubscriber',
    'NewsletterCampaign',
]