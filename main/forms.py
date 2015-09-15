from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from main.models import Trip


class CamperCreateForm(UserCreationForm):
    """Form for registering New Campers"""

    zip = forms.CharField(max_length=10, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class TripCreateForm(ModelForm):
    """Form for creating a new trip"""

    model = Trip
    fields = ('date',)
