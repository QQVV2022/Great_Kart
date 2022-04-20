from django.urls import include, path
# from .views import Home
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('bio/<username>/', views.bio, name='bio'),
    # path('articles/<slug:title>/', views.article, name='article-detail'),
    # path('articles/<slug:title>/<int:section>/', views.section, name='article-section'),
    # path('blog/', include('blog.urls')),

]