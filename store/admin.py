from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(ShippingOrder)
admin.site.register(Cart)
admin.site.register(Guest)
admin.site.register(Brand)
admin.site.register(Review)
admin.site.register(CartItem)