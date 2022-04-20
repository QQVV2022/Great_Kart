from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import re
from .models import Account, UserProfile
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
from django.conf import settings
from carts.views import _cart_id

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import EmailMessage
from django.core.mail import send_mail

# Create your views here.

def register(request):
    return render(request, 'accounts/register.html')

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if not all([first_name, last_name, email, phone_number, password, password2]):
            messages.error(request, "Please input all fields!!")
            return render(request, 'register.html')
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            messages.error(request, "Email address format is wrong!!")
            return render(request, 'register.html')
        if password != password2:
            messages.error(request, "Passwords are not the same!!")
            return render(request, 'register.html')
        username = email.split("@")[0]
        user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        user.phone_number = phone_number
        user.save()

        # Create a user profile
        profile = UserProfile()
        profile.user_id = user.id
        profile.profile_picture = 'userprofile/avatar.png'
        profile.save()

        # user veriation
        current_domain = get_current_site(request)
        mail_subject = 'Please activate your account'
        mail_body = render_to_string('account_veriation_email.html',{
            'user': user,
            'domain': current_domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        # send_email = EmailMessage(mail_subject, mail_body, to=[email])
        # send_email.send()
        email_from = settings.EMAIL_HOST_USER
        send_mail( mail_subject, mail_body, email_from, [email], html_message=mail_body )
    return redirect('/signin/?command=verification&email='+email)

def _cart_combine(request,cart_items_unlog):
    current_user = request.user
    if request.user.is_authenticated:
        try:
            cart_items_log = CartItem.objects.filter(user=current_user)
        except :
            cart_items_log = None
    if not cart_items_log and cart_items_unlog:
        for item in cart_items_unlog:
            item.user = current_user
            item.Cart = None
            item.save()
    elif not cart_items_unlog:
        pass
    else:
        product_variations = []
        for item1 in cart_items_unlog:
            product = item1.product
            varis = list(item1.variations.all())
            product_variations.append([item1.id, item1.quantity, {'product':product, 'varis':varis}])

        for item2 in cart_items_log:
            product = item2.product
            varis = list(item2.variations.all())
            for e in product_variations:
                if {'product':product, 'varis':varis} == e[2]:
                    item2.quantity += e[1]
                    item = CartItem.objects.get(id=e[0])
                    print("==aaa", item)
                    item.delete()
                    item2.save()
                    e[0] = -1

            for e in product_variations:
                if e[0] != -1:
                    item = CartItem.objects.get(id=e[0])
                    item.user = current_user
                    item.cart = None
                    item.save()


def signin(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items_unlog = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        cart_items_unlog = None
        cart = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            _cart_combine(request, cart_items_unlog)
            if cart:
                cart.delete()

            next_page= request.META.get('HTTP_REFERER')
            try:
                url_list = next_page.split("?")[1].split("=")
                ind_of_next = url_list.index("next")
                if ind_of_next >= 0:
                    next_url = url_list[ind_of_next+1].split("&")[0]
                    return redirect(next_url)
            except:
                pass
            return redirect('home')
        else:
            messages.error(request, 'Email or Password is incorrect!!')
    return render(request, 'accounts/signin.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('signin')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


def forget_password(request):
    return render(request, 'accounts/signin.html')


@login_required(login_url = 'signin')
def logout_view(request):
    logout(request)
    return render(request, 'accounts/signin.html')

def forget_password(request):
    return render(request, 'accounts/forget_password.html')

def forget_password_a(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email=email)
        except:
            user = None
        if user:
            # user veriation
            current_domain = get_current_site(request)
            mail_subject = 'Please reset password'
            mail_body = render_to_string('reset_password_email.html',{
                'user': user,
                'domain': current_domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email_from = settings.EMAIL_HOST_USER
            send_mail( mail_subject, mail_body, email_from, [email], html_message=mail_body)
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('signin')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forget_password')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('signin')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('confirm_password')
        if password == password2:
            uid = request.session.get('uid')
            user = Account.objects.get(id=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('signin')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

@login_required(login_url='signin')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user=request.user, is_ordered=True)
    orders_count = orders.count()
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'orders_count': orders_count,
        'userprofile': user_profile,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='signin')
def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user=request.user, is_ordered=True)
    orders.count = orders.count()
    op = OrderProduct.objects.filter(user=request.user)
    for order in orders:
        order.products = op.filter(order=order)
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='signin')
def edit_profile(request):
    profile_form = get_object_or_404(UserProfile, user=request.user)
    user_form = Account.objects.get(id__exact=request.user.id)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        addree1 = request.POST.get('address1')
        addree2= request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        file = request.FILES.get('img')

        if file:
            profile_form.profile_picture = file
        profile_form.address_line_1 = addree1
        profile_form.address_line_2 = addree2
        profile_form.city = city
        profile_form.state = state
        profile_form.zipcode = zipcode
        profile_form.save()

        user_form.first_name = first_name
        user_form.last_name = last_name
        user_form.phone_number = phone
        user_form.save()

        messages.success(request, 'Your profile has been updated.')

    else:
        profile_form = get_object_or_404(UserProfile, user=request.user)

    context = {'profile_form': profile_form,
               'user_form':user_form}
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='signin')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('confirm_password')
        if not all([current_password, new_password, new_password2]):
            messages.error(request, 'Please input required information!')
            return redirect('change_password')
        if new_password != new_password2:
            messages.error(request, 'New passwords are not match!')
            return redirect('change_password')
        user = Account.objects.get(id__exact = request.user.id)
        if not user.check_password(current_password):
            messages.error(request, 'Current passwords is not correct!')
            return redirect('change_password')
        user.set_password(new_password)
        user.save()
        login(request, user)
        messages.success(request, 'Password updated successfully.')
        return redirect('change_password')

    return render(request, 'accounts/change_password.html')

@login_required(login_url='signin')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)