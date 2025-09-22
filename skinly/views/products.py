from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from skinly.models import Product, Review, SkinType, ProductType, SearchEngine, Brand


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
