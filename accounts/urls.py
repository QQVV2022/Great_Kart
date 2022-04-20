from django.urls import include, path
# from .views import Home
from . import views

urlpatterns = [
    path('signin/', views.signin, name='signin'),
    # path('signin_a/', views.signin_a, name='signin_a'),
    path('signup/', views.signup, name='signup'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('forgetpassword/', views.forget_password, name='forget_password'),
    path('forget_password_a/', views.forget_password_a, name='forget_password_a'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<order_id>', views.order_detail, name='order_detail'),

]