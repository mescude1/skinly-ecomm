from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from skinly.models import CartItem, Cart, Product


@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if product.stock_quantity < quantity:
        messages.error(request, 'Not enough stock available')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Not enough stock available'})
        return redirect('skinly:product_detail', product_id=product_id)

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

    return redirect('skinly:cart')


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

    # Get recommended products based on cart items
    recommended_products = []
    if cart_items:
        # Get brands and product types from cart items
        cart_brands = set(item.product.brand for item in cart_items)
        cart_product_types = set(item.product.product_type for item in cart_items)
        cart_product_ids = set(item.product.id for item in cart_items)

        # Find similar products by brand or product type
        similar_products = Product.objects.filter(
            Q(brand__in=cart_brands) | Q(product_type__in=cart_product_types),
            stock_quantity__gt=0
        ).exclude(id__in=cart_product_ids)

        # Get user's skin type for better recommendations
        if request.user.skin_type:
            similar_products = similar_products.filter(
                Q(skin_type_compatibility__isnull=True) |
                Q(skin_type_compatibility=request.user.skin_type)
            )

        # Order by rating and limit to 4 products
        recommended_products = similar_products.order_by('-rating', '?')[:4]

    context = {
        'cart_items': cart_items,
        'total': total,
        'shipping': shipping,
        'tax': tax,
        'final_total': final_total,
        'free_shipping_needed': free_shipping_needed,
        'recommended_products': recommended_products,
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

    return redirect('skinly:cart')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('skinly:cart')