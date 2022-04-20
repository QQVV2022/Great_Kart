from django.shortcuts import render
from django.views import View
from store.models import Product, ReviewRating
from django.db.models import Avg, Count

# Create your views here.

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    for p in products:
        reviews = ReviewRating.objects.filter(product=p, status=True)
        avg_rating = reviews.aggregate(Avg('rating'))
        if not avg_rating['rating__avg']:
            avg_rating = {'rating__avg': 0}
        p.avg_rating = avg_rating['rating__avg']
        p.count = reviews.aggregate(Count('rating'))['rating__count']
    context = {'products': products }
    return render(request,"index.html", context)

