from .models import Category

def get_categories(request):
    links = Category.objects.all()
    return dict(links=links)