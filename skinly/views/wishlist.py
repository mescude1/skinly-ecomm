from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_POST

from skinly.models import Product


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
    return redirect('skinly:product_detail', product_id=product_id)