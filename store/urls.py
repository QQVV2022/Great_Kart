from django.urls import include, path
# from .views import Home
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('search/', views.search, name='search'),
    path('submit_review/<product_id>', views.submit_review, name='submit_review'),
    path('<slug:category_slug>/', views.store, name='category'),
    path('<category_slug>/<product_slug>/', views.product_detail, name='detail'),
]