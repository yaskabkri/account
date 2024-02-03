# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from prd.models import Staff

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_num = forms.CharField(max_length=30, required=True)
    position = forms.CharField(max_length=255, required=True)
    national_id = forms.CharField(max_length=255, required=True)

    class Meta:
        model = Staff
        fields = ('user', 'email', 'password1', 'password2', 'first_name', 'last_name', 'position', 'phone_num', 'national_id')


