from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'skinly'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search_products, name='search_products'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('toggle-wishlist/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Reviews
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # Contact
    path('contact/', views.contact_view, name='contact'),
    
    # FAQ Pages
    path('shipping/', views.shipping_info_view, name='shipping_info'),
    path('returns/', views.returns_view, name='returns'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]