from django.shortcuts import render, redirect
from skinly.models import Product, RecommendationEngine


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
    return redirect('skinly:home')