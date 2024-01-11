from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.store, name = 'store'),
    path('cart/', views.cart, name = 'cart'),
    path('checkout/', views.checkout, name = 'checkout'),
    path('category/', views.category, name = 'category'),
    path('search/', views.search, name = 'search'),
    path('login/', views.login_, name = 'login'),
    path('logout/', views.logout_, name = 'logout'),
    path('register/', views.register, name = 'register'),
    path('product/<int:product_id>/', views.product, name = 'product'),
    path('submit_review/<int:product_id>/', views.submit_review, name = 'submit_review'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name = 'add_to_cart')
]