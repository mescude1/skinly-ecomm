from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import home
from .views import products
from .views import cart
from .views import checkout
from .views import wishlist
from .views import orders
from .views import reviews
from .views import signup
from .views import logout
from .views import support

app_name = 'skinly'

urlpatterns = [
    # Home
    path('', home.home, name='home'),
    path('index/', home.index, name='index'),
    
    # Products
    path('products/', products.product_list, name='product_list'),
    path('products/<int:product_id>/', products.product_detail, name='product_detail'),
    path('search/', products.search_products, name='search_products'),
    
    # Cart
    path('cart/', cart.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', cart.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', cart.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', cart.remove_from_cart, name='remove_from_cart'),
    
    # Wishlist
    path('wishlist/', wishlist.wishlist_view, name='wishlist'),
    path('toggle-wishlist/<int:product_id>/', wishlist.toggle_wishlist, name='toggle_wishlist'),
    
    # Orders
    path('checkout/', checkout.checkout_view, name='checkout'),
    path('orders/', orders.order_list, name='order_list'),
    path('orders/<int:order_id>/', orders.order_detail, name='order_detail'),
    
    # Reviews
    path('add-review/<int:product_id>/', reviews.add_review, name='add_review'),
    
    # Profile
    path('profile/', support.profile_view, name='profile'),
    
    # Contact
    path('contact/', support.contact_view, name='contact'),
    
    # FAQ Pages
    path('shipping/', support.shipping_info_view, name='shipping_info'),
    path('returns/', support.returns_view, name='returns'),
    
    # Legal Pages
    path('privacy-policy/', support.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', support.terms_of_service_view, name='terms_of_service'),
    
    # Newsletter
    path('newsletter/subscribe/', support.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', signup.signup_view, name='signup'),
    path('logout/', logout.logout_view, name='logout'),
]