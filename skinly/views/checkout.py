from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from skinly.models import Cart, ShippingAddress, Order, OrderItem, InventoryManager


@login_required
def checkout_view(request):
    """Checkout page"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cart_items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty')
        return redirect('skinly:cart')

    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('skinly:cart')

    # Calculate totals
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = 0 if subtotal >= 50 else Decimal('5.99')
    tax = subtotal * Decimal('0.08')
    total = subtotal + shipping + tax

    # Get user's shipping addresses
    shipping_addresses = request.user.shipping_addresses.all()

    if request.method == 'POST':
        # Process order
        payment_method = request.POST.get('payment_method')
        shipping_address_id = request.POST.get('shipping_address')

        if not shipping_address_id:
            messages.error(request, 'Please select a shipping address')
            return redirect('skinly:checkout')

        try:
            shipping_address = request.user.shipping_addresses.get(id=shipping_address_id)
        except ShippingAddress.DoesNotExist:
            messages.error(request, 'Invalid shipping address')
            return redirect('skinly:checkout')

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=f"{shipping_address.address_line_1}, {shipping_address.city}, {shipping_address.state} {shipping_address.zip_code}",
            phone_number=shipping_address.phone_number or '',
            total_price=total,
            payment_method=payment_method,
            status='PENDING'
        )

        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

            # Update product stock
            cart_item.product.stock_quantity -= cart_item.quantity
            cart_item.product.save()

        # Clear cart
        cart_items.delete()

        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('skinly:order_detail', order_id=order.id)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'shipping_addresses': shipping_addresses,
    }
    return render(request, 'skinly/checkout.html', context)

@login_required
def checkout(request):
    """Checkout page"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cart_items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty')
        return redirect('skinly:cart')

    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('skinly:cart')

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
        return redirect('skinly:order_detail', order_id=order.id)

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'skinly/checkout.html', context)