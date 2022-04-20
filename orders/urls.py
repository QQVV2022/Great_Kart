from django.urls import include, path
from . import views

urlpatterns = [

    path('placeorder/', views.place_order, name='place_order'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('payments', views.payments, name='payments'),
]