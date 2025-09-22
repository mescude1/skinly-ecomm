from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from skinly.models import Product, Review, RecommendationEngine


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
    return redirect('skinly:product_detail', product_id=product_id)
