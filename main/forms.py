from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from main.models import Trip
import datetime
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm, Form

date_field = forms.DateField(widget=SelectDateWidget)

class CamperCreateForm(UserCreationForm):
    """Form for Registering new Campers"""
    zip = forms.CharField(max_length=10, required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class TripCreateForm(ModelForm):
    model = Trip
    fields = ('date')

