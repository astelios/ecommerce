from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review

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
            'user': forms.HiddenInput(),  # Assuming you'll handle user association in the view
            'product': forms.HiddenInput(),  # Assuming you'll handle product association in the view
            'rating': forms.Select(choices=Review.RATING_CHOICES, attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

class ShippingOrderForm(forms.Form):
    name = forms.CharField(max_length=200)
    email = forms.EmailField()
    address = forms.CharField(max_length=200)
    city = forms.CharField(max_length=200)
    state = forms.CharField(max_length=200)
    country = forms.CharField(max_length=200)