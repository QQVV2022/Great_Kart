from .models import CartItem, Cart
from carts.views import _cart_id

def cart_total_count(request):
    if request.user.is_authenticated:
        if 'admin' in request.path:
            return {}
        count = CartItem.objects.filter(user=request.user).count()
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            count = CartItem.objects.filter(cart=cart).count()
        except Cart.DoesNotExist:
            return {}
    return dict(cart_count=count)