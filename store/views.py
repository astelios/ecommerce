from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Avg
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from .forms import *
import secrets

def generate_random_cookie():
    while True:
        # Generate a random cookie value
        random_cookie_value = secrets.token_hex(16)

        # Check if the generated value is unique
        if not Guest.objects.filter(cookie=random_cookie_value).exists():
            return random_cookie_value


# Returns cookie value and cart instance 
def cookie_and_cart(request):
    cookie_value = request.COOKIES.get('user_cookie', '')

    try:
        guest_instance = Guest.objects.get(cookie=cookie_value)
        cart_instance = guest_instance.cart
    except Guest.DoesNotExist:
        cart_instance = Cart.objects.create(number_of_items=0)
        cookie_value = generate_random_cookie()
        Guest.objects.create(cart=cart_instance ,cookie=cookie_value)      

    return cookie_value, cart_instance

def get_guest(request):
    cookie_value = request.COOKIES.get('user_cookie', '')
    return Guest.objects.get(cookie=cookie_value)


# build store with provided filtered products/categories
def build_store_cookie(request, products):
    cookie_value, cart_instance = cookie_and_cart(request)
    categories = Category.objects.all()
    brands = Brand.objects.all()
    context = {'products' : products, 'categories' : categories, 'cart' : cart_instance, 'brands' : brands}
    response = render(request, 'store/store.html', context)
    response.set_cookie('user_cookie', cookie_value)

    return response


############################### Create your views here. ###############################

def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create()
        items = cart.cartitem_set.all()
    else:
        items = []
        cart = None
    context={'items':items, 'cart': cart}

    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create()
        items = cart.cartitem_set.all()
    else:
        items = []
        cart = None
    context={'items':items, 'cart': cart, 'form':ShippingOrderForm()}

    return render(request, 'store/checkout.html', context)

def logout_(request):
    logout(request)
    return(store(request))


def login_(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return store(request)
        else:
            form.add_error(None, 'Invalid username or password')
        
    else:
        form = AuthenticationForm()

    return render(request, 'store/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Redirect to login
            form = AuthenticationForm()
            return render(request, 'store/login.html', {'form': form})
    else:
        form = RegistrationForm()

    return render(request, 'store/register.html', {'form': form})

def product(request, product_id):
    
    product = Product.objects.get(id=product_id)
    cookie_value, cart = cookie_and_cart(request)
    reviews = Review.objects.filter(product__id=product_id)
    avg_rating = reviews.aggregate(Avg("rating", default=0))
    context = {'product' : product, 'cart' : cart, 'reviews' : reviews, 'avg_rating' : avg_rating, 'form' : ReviewForm()}

    return render(request, 'store/product.html', context)

@login_required
def submit_review(request, product_id):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Set the user and product fields before saving
            review = form.save(commit=False)
            review.user = request.user  # Set the current logged-in user
            review.product = Product.objects.get(id=product_id)  # Set the specific product
            review.save()
    else:
        form = ReviewForm()

    return product(request, product_id)

def add_to_cart(request, product_id):
    cookie_value, cart_instance = cookie_and_cart(request)
    product_instance = Product.objects.get(id=product_id)

    try:
        cart_item_instance = CartItem.objects.get(product__id=product_id, cart=cart_instance)
        
        if cart_item_instance.quantity < product_instance.stock:
            print(cart_item_instance.quantity)
            print(product_instance.stock)
            cart_item_instance.quantity += 1
            cart_item_instance.save()
            cart_instance.number_of_items += 1
            cart_instance.save()
        else:
            return redirect(request.META.get('HTTP_REFERER', '/'))

    except CartItem.DoesNotExist:
        if product_instance.stock > 0:
            cart_item_instance = CartItem.objects.create(cart=cart_instance, product=product_instance, quantity=1)
            cart_instance.number_of_items += 1
            cart_instance.save()
        else:
            return redirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponse(status=204) # response for success

def remove_from_cart(request, product_id):
    cookie_value, cart_instance = cookie_and_cart(request)
    product_instance = Product.objects.get(id=product_id)

    cart_instance.number_of_items -= 1
    cart_instance.save()

    cart_item_instance = CartItem.objects.get(product__id=product_id, cart=cart_instance)
    cart_item_instance.quantity -= 1
    cart_item_instance.save()
    if cart_item_instance.quantity == 0:
        cart_item_instance.delete()

    return HttpResponse(status=204) # response for success


# Store template

def store(request):
    products = Product.objects.all()

    return build_store_cookie(request, products)

def category(request):
    q = request.GET.get('q', '')
    id = Category.objects.get(name=q)

    products = Product.objects.filter(category_id=id)

    return build_store_cookie(request, products)

def search(request):
    # Query for searchField
    searchField = request.POST["searchField"]
    products = Product.objects.filter(name__icontains=searchField)

    # Query for categories
    categoryQueryList = []
    for instance in Category.objects.all():
        field_value = request.POST.get(instance.name, '')
        if field_value:
            id = Category.objects.get(name=instance.name)
            categoryQueryList.append(id.id)
    if categoryQueryList:
        products = products.filter(category__id__in=categoryQueryList)

    # Query for brands
    brandQueryList = []
    for instance in Brand.objects.all():
        field_value = request.POST.get(instance.name, '')
        if field_value:
            id = Brand.objects.get(name=instance.name)
            brandQueryList.append(id.id)
    if brandQueryList:
        products = products.filter(brand__id__in=brandQueryList)

    # Query for price range and availability
    priceStart = request.POST.get("priceStart", "")
    if priceStart:
        products = products.filter(price__gte=float(priceStart))
    priceEnd = request.POST.get("priceEnd", "")
    if priceEnd:
        products = products.filter(price__lte=float(priceEnd))
    if request.POST.get("availability", ""):
        products = products.filter(stock__gt=0)

    return build_store_cookie(request, products)

def shipping_order(request):
    form = ShippingOrderForm(request.POST)
    print(form.is_valid())
    print(form)
    if form.is_valid():
        # Create shippingOrder
        shippingOrder = form.save(commit=False)
        shippingOrder.guest = get_guest(request)
        shippingOrder.save()

        # Create orderItems
        cartItems = CartItem.objects.filter(cart=shippingOrder.guest.cart)
        for cartItem in cartItems:
            shippingOrder.guest.cart.number_of_items -= cartItem.quantity
            cartItem.product.stock -= cartItem.quantity
            cartItem.product.save()
            OrderItem.objects.create(product=cartItem.product, shippingOrder=shippingOrder, quantity=cartItem.quantity)
            cartItem.delete()
        shippingOrder.guest.cart.save()

        return store(request)
    else:
        return checkout(request)
    
def order(request, order_id):
    order_instance = ShippingOrder.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(shippingOrder=order_instance)
    context = {'order' : order_instance, 'items' : order_items, 'cart' : get_guest(request).cart}

    return render(request, 'store/order.html', context)

def order_history(request):
    guest_ = get_guest(request)

    try:
        shipping_orders = ShippingOrder.objects.filter(guest=guest_)
        context = {'items' : shipping_orders, 'cart' : guest_.cart}
    except ShippingOrder.DoesNotExist:
        context = {'cart' : guest_.cart}

    return render(request, 'store/order_history.html', context)