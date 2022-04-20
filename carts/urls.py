from django.urls import include, path
# from .views import Home
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('check_out/', views.check_out, name='check_out'),
    path('add/<product_id>', views.add_cart, name='add_cart'),
    path('remove_cart/<cart_item_id>',views.remove_cart, name='remove_cart'),
    path('increase/<cart_item_id>', views.increase_cart, name='increase_cart'),
    path('decrease/<cart_item_id>', views.decrease_cart, name='decrease_cart'),

]