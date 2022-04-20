from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from category.models import Category
from accounts.models import UserProfile
from .models import Product, Variation, ReviewRating, ProductGallery
from django.db.models import Avg, Count
from .forms import ReviewForm


# Create your views here.
def store(request, category_slug=None):
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category).order_by('id')
    else:
        products = Product.objects.all().order_by('id')
    products_count = len(products)

    paginator = Paginator(products, 3) # Show 3 contacts per page.
    page_number = request.GET.get('page')
    if not page_number or int(page_number) > paginator.num_pages:
        page_number = 1
    page_obj = paginator.get_page(page_number)

    context = {'products_count':products_count,
               'products': page_obj}

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    category = get_object_or_404(Category,slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category = category)
    # product.colors = Variation.objects.filter(product=product, variation_category='color')
    # product.sizes = Variation.objects.filter(product=product, variation_category='size')
    v = Variation.objects.filter(product=product)
    product.colors = v.filter(variation_category='color')
    product.sizes = v.filter(variation_category='size')
    reviews = ReviewRating.objects.filter(product=product, status=True)
    for review in reviews:
           review.user_profile = UserProfile.objects.get(user_id=review.user.id)
    product.avg_rating = reviews.aggregate(Avg('rating'))
    product.count = reviews.aggregate(Count('rating'))
    product_gallery = ProductGallery.objects.filter(product=product)

    context = {'category':category,
               'product':product,
               'reviews':reviews,
               'product_gallery': product_gallery
               }

    return render(request, 'store/product-detail.html', context)

def search(request):
    key_word = request.GET.get('keyword')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if not key_word and min_price=='' and max_price=='':
        redirect('store')
    context = {}

    if not min_price:
        min_price = 0
    else:
        min_price = float(min_price)
    if not max_price or max_price == '2000':
        max_price = 9999999999
        max_price = float(max_price)
    else:
        if not key_word:
            key_word=''
    products = Product.objects.filter(
        (Q(product_name__contains=key_word) | Q(description__contains=key_word)) &  Q(price__gte = min_price) & Q(price__lte = max_price)
    ).order_by('id')

        # paginator = Paginator(products, 3) # Show 3 contacts per page.
        # page_number = request.GET.get('page')
        # if not page_number or int(page_number) > paginator.num_pages:
        #     page_number = 1
        # page_obj = paginator.get_page(page_number)

    products_count = products.count()
    context = {'products_count':products_count,
                    'products': products}

    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user=request.user, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']  # new
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id  # new
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
        return redirect(url)
