from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from decimal import Decimal
import json

from .models import (
    Product, Brand, Color, User, Cart, CartItem, Order, OrderItem,
    Review, TasteProfile, RecommendationEngine, SearchEngine,
    InventoryManager, SkinType, SkinTone, ProductType, FinishType
)
from .forms import SignUpForm

def home(request):
    """Home page with featured products and recommendations"""
    featured_products = Product.objects.filter(stock_quantity__gt=0)[:8]
    
    recommendations = []
    if request.user.is_authenticated:
        engine = RecommendationEngine.objects.first()
        if engine:
            recommendations = engine.generate_recommendations(request.user, limit=6)
    
    context = {
        'featured_products': featured_products,
        'recommendations': recommendations,
    }
    return render(request, 'skinly/home.html', context)

def index(request):
    return redirect('home')

def product_list(request):
    """Product catalog page with filtering and search"""
    products = Product.objects.filter(stock_quantity__gt=0)
    brands = Brand.objects.all()
    
    # Filter by query
    query = request.GET.get('q', '')
    if query:
        search_engine = SearchEngine.objects.first()
        if search_engine:
            products = search_engine.search(query)
        else:
            products = products.filter(
                Q(name__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(product_type__icontains=query)
            )
    
    # Filter by brand
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = products.filter(brand_id=brand_filter)
    
    # Filter by product type
    product_type_filter = request.GET.get('product_type')
    if product_type_filter:
        products = products.filter(product_type=product_type_filter)
    
    # Filter by skin type
    skin_type_filter = request.GET.get('skin_type')
    if skin_type_filter:
        products = products.filter(
            Q(skin_type_compatibility__isnull=True) |
            Q(skin_type_compatibility=skin_type_filter)
        )
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(price__lte=Decimal(max_price))
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'brands': brands,
        'product_types': ProductType.choices,
        'skin_types': SkinType.choices,
        'query': query,
        'current_filters': {
            'brand': brand_filter,
            'product_type': product_type_filter,
            'skin_type': skin_type_filter,
            'min_price': min_price,
            'max_price': max_price,
        }
    }
    return render(request, 'skinly/product_list.html', context)

def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Get user's review if authenticated
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(user=request.user, product=product)
        except Review.DoesNotExist:
            pass
    
    # Get similar products
    similar_products = Product.objects.filter(
        Q(brand=product.brand) | Q(product_type=product.product_type),
        stock_quantity__gt=0
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'user_review': user_review,
        'similar_products': similar_products,
    }
    return render(request, 'skinly/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if product.stock_quantity < quantity:
        messages.error(request, 'Not enough stock available')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Not enough stock available'})
        return redirect('product_detail', product_id=product_id)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'{product.name} added to cart'})
    
    return redirect('cart')

@login_required
def cart_view(request):
    """Shopping cart page"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cart_items.all()
    except Cart.DoesNotExist:
        cart_items = []
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Calculate shipping
    shipping = Decimal('0.00') if total >= 50 else Decimal('5.99')
    
    # Calculate tax (8%)
    tax = total * Decimal('0.08')
    
    # Calculate final total
    final_total = total + shipping + tax
    
    # Calculate free shipping needed
    free_shipping_needed = max(Decimal('0.00'), Decimal('50.00') - total)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'shipping': shipping,
        'tax': tax,
        'final_total': final_total,
        'free_shipping_needed': free_shipping_needed,
    }
    return render(request, 'skinly/cart.html', context)

@login_required
@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
    elif quantity <= cart_item.product.stock_quantity:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated')
    else:
        messages.error(request, 'Not enough stock available')
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('cart')

@login_required
def wishlist_view(request):
    """Wishlist page"""
    wishlist_products = request.user.wishlist.all()
    
    context = {
        'wishlist_products': wishlist_products,
    }
    return render(request, 'skinly/wishlist.html', context)

@login_required
@require_POST
def toggle_wishlist(request, product_id):
    """Add/remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    if product in request.user.wishlist.all():
        request.user.wishlist.remove(product)
        action = 'removed'
    else:
        request.user.wishlist.add(product)
        action = 'added'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'action': action})
    
    messages.success(request, f'Product {action} to/from wishlist')
    return redirect('product_detail', product_id=product_id)

@login_required
def checkout(request):
    """Checkout page"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cart_items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_price=total
        )
        
        # Create order items and reduce stock
        inventory_manager = InventoryManager.objects.first()
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Reduce stock
            if inventory_manager:
                inventory_manager.reduce_stock(cart_item.product.id, cart_item.quantity)
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'skinly/checkout.html', context)

@login_required
def order_list(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'skinly/order_list.html', context)

@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'skinly/order_detail.html', context)

@login_required
@require_POST
def add_review(request, product_id):
    """Add product review"""
    product = get_object_or_404(Product, id=product_id)
    rating = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '')
    
    review, created = Review.objects.update_or_create(
        user=request.user,
        product=product,
        defaults={
            'rating': rating,
            'comment': comment,
        }
    )
    
    # Update product rating
    avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    product.rating = avg_rating or 0
    product.save()
    
    # Update taste profile with recommendation engine
    engine = RecommendationEngine.objects.first()
    if engine:
        feedback = 'positive' if rating >= 4 else 'negative'
        engine.update_taste_profile(request.user, product, feedback)
    
    action = 'updated' if not created else 'added'
    messages.success(request, f'Review {action} successfully')
    return redirect('product_detail', product_id=product_id)

@login_required
def profile_view(request):
    """User profile page"""
    if request.method == 'POST':
        # Update profile
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.skin_tone = request.POST.get('skin_tone', '')
        request.user.skin_type = request.POST.get('skin_type', '')
        request.user.save()
        
        # Update taste profile
        taste_profile, created = TasteProfile.objects.get_or_create(
            user=request.user,
            defaults={'user': request.user}
        )
        
        if not request.user.taste_profile:
            request.user.taste_profile = taste_profile
            request.user.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    context = {
        'skin_tones': SkinTone.choices,
        'skin_types': SkinType.choices,
    }
    return render(request, 'skinly/profile.html', context)

def search_products(request):
    """AJAX search for products"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    search_engine = SearchEngine.objects.first()
    if search_engine:
        products = search_engine.search(query)[:10]
    else:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(brand__name__icontains=query),
            stock_quantity__gt=0
        )[:10]
    
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'brand': product.brand.name,
            'price': float(product.price),
            'image_url': '/static/images/placeholder.jpg',  # Add image field to model later
        })
    
    return JsonResponse({'products': product_data})

def contact_view(request):
    """Contact us page with company information"""
    return render(request, 'skinly/contact.html')

def shipping_info_view(request):
    """Shipping information FAQ page"""
    return render(request, 'skinly/shipping_info.html')

def returns_view(request):
    """Returns policy FAQ page"""
    return render(request, 'skinly/returns.html')

@require_POST
def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    from .models import NewsletterSubscriber
    import logging
    
    logger = logging.getLogger(__name__)
    
    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip()
    
    logger.info(f"Newsletter subscription attempt for email: {email}")
    
    if not email:
        messages.error(request, 'Please provide a valid email address.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'name': name, 'is_active': True}
        )
        
        if created:
            messages.success(request, 'Thank you for subscribing to our newsletter! You\'ll receive the latest beauty tips and exclusive offers.')
            logger.info(f"New newsletter subscriber created: {email}")
        else:
            if subscriber.is_active:
                messages.info(request, 'You\'re already subscribed to our newsletter!')
                logger.info(f"Existing active subscriber tried to subscribe again: {email}")
            else:
                subscriber.is_active = True
                subscriber.save()
                messages.success(request, 'Welcome back! Your newsletter subscription has been reactivated.')
                logger.info(f"Reactivated newsletter subscriber: {email}")
    
    except Exception as e:
        logger.error(f"Newsletter subscription error for {email}: {str(e)}")
        messages.error(request, 'There was an error processing your subscription. Please try again.')
    
    # Return to the page where the form was submitted
    return redirect(request.META.get('HTTP_REFERER', '/'))

def signup_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('skinly:home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Welcome to Skinly.')
            login(request, user)
            return redirect('skinly:home')
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def logout_view(request):
    """Handle user logout for both GET and POST requests"""
    # Only log out if user is actually authenticated
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
    return redirect('skinly:home')
