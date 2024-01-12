from django.shortcuts import render
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
    # if cookie_value:
    #     guest_instance = Guest.objects.get(cookie=cookie_value)
    #     cart_instance = guest_instance.cart
    # else:
    #     cart_instance = Cart.objects.create(number_of_items=0)
    #     cookie_value = generate_random_cookie()
    #     Guest.objects.create(cart=cart_instance ,cookie=cookie_value)  

    try:
        guest_instance = Guest.objects.get(cookie=cookie_value)
        cart_instance = guest_instance.cart
    except Guest.DoesNotExist:
        cart_instance = Cart.objects.create(number_of_items=0)
        cookie_value = generate_random_cookie()
        Guest.objects.create(cart=cart_instance ,cookie=cookie_value)      

    return cookie_value, cart_instance

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
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create()
        items = cart.cartitem_set.all()
    else:
        items = []
        cart = None
    context={'items':items, 'cart': cart}

    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create()
        items = cart.cartitem_set.all()
    else:
        items = []
        cart = None
    context={'items':items, 'cart': cart}

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

    cart_instance.number_of_items += 1
    cart_instance.save()

    try:
        cart_item_instance = CartItem.objects.get(product__id=product_id, cart=cart_instance)

        cart_item_instance.quantity += 1
        cart_item_instance.save()
    except CartItem.DoesNotExist:
        cart_item_instance = CartItem.objects.create(cart=cart_instance, product=product_instance, quantity=1)

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
    if request.method == 'POST':
        form = ShippingOrderForm(request.POST)
        if form.is_valid():
            # Save data to the database
            shipping_order = ShippingOrder(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                country=form.cleaned_data['country']
            )
            shipping_order.save()

            # Redirect to a success page or do something else
            return JsonResponse({'success': True})
    # else:
    #     form = ShippingOrderForm()

    # return render(request, 'shipping.html', {'form': form})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)