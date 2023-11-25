from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Customer

# class UserForm(ModelForm):
#     class Meta:
#         model=User
#         fields=['name','email']

class UserForm(ModelForm):
    class Meta:
        model=Customer
        fields=['name','email']
         