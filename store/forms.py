from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, ShippingOrder

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['user', 'product', 'rating', 'comment']

        widgets = {
            'user': forms.HiddenInput(),  
            'product': forms.HiddenInput(),
            'rating': forms.Select(choices=Review.RATING_CHOICES, attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

class ShippingOrderForm(forms.ModelForm):
    class Meta:
        model = ShippingOrder
        exclude = ['guest']
        fields = ['name', 'email', 'address', 'city', 'state', 'zip_code']
        widgets = {
            'name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':  forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }