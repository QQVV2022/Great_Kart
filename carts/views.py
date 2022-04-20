from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from store.models import Product, Variation
from .models import Cart, CartItem
from accounts.models import Account

# Create your views here.
def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

def cart(request):  # show the cart
    total_price = 0
    cart_items = None
    if request.user.is_authenticated:
        try:
            cart_items = CartItem.objects.filter(user=request.user)
            for item in cart_items:
                total_price += item.sub_total_price()
        except Exception as e:
            print(e)
        tax = round(total_price * 0.1, 2) if total_price else 0
        total = round(total_price + total_price * 0.1, 2) if total_price else 0
        # print("1===cart view cart",cart_items)
        context = {'cart_items':cart_items,
               'total_price': total_price,
               'tax': tax,
               'total': total
               }
        return render(request, 'cart.html', context)
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            # print("==1", cart)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            total_price += item.sub_total_price()
        tax = round(total_price * 0.1, 2) if total_price else 0
        total = round(total_price + total_price * 0.1, 2) if total_price else 0
        # print("2===cart view cart",cart_items)
        context = {'cart_items':cart_items,
               'total_price': total_price,
               'tax': tax,
               'total': total
               }
        return render(request, 'cart.html', context)


def add_cart(request, product_id):  # add product to the cart
    product = get_object_or_404(Product, id=product_id)
    v = Variation.objects.filter(product=product)
    if request.method == 'POST':
        product_variation = []
        for key in request.POST:
            if key == 'csrfmiddlewaretoken':
                continue
            vari_v = request.POST.get(key)
            variation = v.filter(variation_category=key, variation_value=vari_v, product=product)
            product_variation.append(variation)
            # print("=====1",vari_v, product_variation)

    if request.user.is_authenticated:
        items_exists = CartItem.objects.filter(product=product, user=request.user).exists()
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()
        items_exists = CartItem.objects.filter(cart=cart, product=product).exists()

    if items_exists:
        if request.user.is_authenticated:
            items = CartItem.objects.filter(product=product, user=request.user)
        else:
            items = CartItem.objects.filter(cart=cart, product=product)

        is_item_exists_id = 0
        for item in items:
            varis = list(item.variations.all())
            j = 0
            # print("===2", varis,product_variation,is_item_exists_id)
            if not is_item_exists_id:
                for i, e in enumerate(product_variation, start=1):
                    # print("===3", list(e))
                    if list(e)[0] in varis:
                        print("===4",i,j)
                        j += 1
                    if j == i:
                        is_item_exists_id = item.id
                        # print("==5",is_item_exists_id)
        if is_item_exists_id != 0:
            # print("===6",item.quantity)
            item = CartItem.objects.get(id=is_item_exists_id)
            item.quantity += 1
            # print(item.quantity)
            item.save()
        else:
            if request.user.is_authenticated:
                item = CartItem.objects.create(product=product, quantity=1, user=request.user)
                item.save()
            else:
                item = CartItem.objects.create(cart=cart, product=product, quantity=1)

            item.variations.clear()
            if len(product_variation)>0:
                for vari in product_variation:
                    item.variations.add(*vari)  # unpack 'model'
            item.save()
    else:
        if request.user.is_authenticated:
            item = CartItem.objects.create(product=product, quantity=1, user=request.user)
        else:
            item = CartItem.objects.create(cart=cart, product=product, quantity=1)

        item.variations.clear()
        if len(product_variation) > 0:
            for vari in product_variation:
                item.variations.add(*vari)  # unpack 'model'
        item.save()

    return redirect('cart') # HttpResponse("hhhh")

def remove_cart(request, cart_item_id):
    try:
        c = CartItem.objects.get(id=cart_item_id).delete()
    except Exception as e:
        print(e)
        return HttpResponse(e)
    return redirect('cart')

def increase_cart(request, cart_item_id):
    item = get_object_or_404(CartItem, id=cart_item_id)
    if item.quantity <= 0:
        item.quantity = 1
    else:
        item.quantity += 1
    item.save()
    return redirect('cart')


def decrease_cart(request, cart_item_id):
    item = get_object_or_404(CartItem, id=cart_item_id)
    if item.quantity == 1:
        return redirect('remove_cart', cart_item_id)
    else:
        item.quantity -= 1
    item.save()
    return redirect('cart')

@login_required(login_url = 'signin')
def check_out(request):
    total_price = 0
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        total_price += item.sub_total_price()
    tax = round(total_price * 0.1, 2) if total_price else 0
    total = round(total_price + total_price * 0.1, 2) if total_price else 0

    context = {'cart_items':cart_items,
               'total_price': total_price,
               'tax': tax,
               'total': total
               }
    return render(request, 'orders/place-order.html', context)


