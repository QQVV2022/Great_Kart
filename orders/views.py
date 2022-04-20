import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderProduct, Payment
from store.models import Product
from datetime import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# Create your views here.
@login_required(login_url = 'signin')
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    if not cart_items:
        return redirect('store')
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        order_note = request.POST.get('order_note')
        # payment_option = request.POST.get('payment-option')

        if not all([first_name, last_name, email, phone, address_line_1, city, state, zipcode]):
            messages.error(request, "please fill the address form!")
            return render(request, 'orders/place-order.html')

        total_price = 0
        for item in cart_items:
            total_price += item.sub_total_price()
        tax = round(total_price * 0.1, 2) if total_price else 0
        total = round(total_price + total_price * 0.1, 2) if total_price else 0

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        # ip = request.META.get('REMOTE_ADDR')

        order_date = datetime.now().strftime("%Y%m%d")
        newo = Order.objects.create(user=current_user,first_name=first_name,last_name=last_name,phone=phone,email=email,
                             address_line_1=address_line_1,address_line_2=address_line_2,city=city,state=state,zipcode=zipcode,order_note=order_note,
                             order_total=total,tax=tax,ip=ip)
        order_number = order_date + str(newo.id)
        newo.order_number = order_number
        newo.save()
        order = Order.objects.get(id = newo.id)
        context = {'order':order,
                   'cart_items':cart_items,
                   'total_price': total_price,
                   'tax': tax,
                   'total': total
                   }
        return render(request, 'orders/place-order-final.html', context)
    return redirect('check_out')


@login_required(login_url = 'signin')
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(order_number=body['orderID'], user=request.user)

    payment = Payment(user=request.user, payment_id=body['transID'],
                      payment_method=body['payment_method'],status=body['status'],amount_paid=order.order_total)
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.user = request.user
        order_product.product = item.product
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=order_product.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    cart_items.delete()  # after move cart items to the order products, delete cart items

    mail_subject = 'Thank you for your order!'
    mail_body = render_to_string('order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, mail_body, to=[to_email])
    send_email.send()

    context = {
        'order_number': order.order_number,
        'trans_id': payment.payment_id
    }
    return JsonResponse(context)



@login_required(login_url = 'signin')
def order_complete(request):
    order_no = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')
    print('order_no,payment_id',order_no,payment_id)
    try:
        order = Order.objects.get(order_number=order_no)
        order_products = OrderProduct.objects.filter(order=order)
        payment = Payment.objects.get(payment_id=payment_id)
        sub_total = 0
        for e in order_products:
            sub_total += e.product.price * e.quantity

        context = {
            'order_products':order_products,
            'payment': payment,
            'payment_id': payment_id,
            'sub_total': sub_total,
            'order_number': order_no,
            'order': order,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')



