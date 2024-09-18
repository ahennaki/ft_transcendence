from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .random import random_passwd

User = get_user_model()

def AuthenticateUser42(request, data):
    email = data['email']
    username = data['login']
    # to add picture
    # first name last name
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(username=username, email=email, password=random_passwd())
    return user.id