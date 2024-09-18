from django.core.management.base import BaseCommand
from faker import Faker
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # Replace 'your_project_name' with your actual project name
django.setup()


from authentication.models import CustomUser  # Update this with the actual app and model

fake = Faker()
for _ in range(50):
    user = CustomUser.objects.create_user(
        username=fake.user_name(),
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        password=fake.password()
    )
        # Set hashed password
    password=fake.password()
    user.set_password(password)
    
    # Save user to the database
    user.save()
    print(f"Created user: {user.username} + {password}")
