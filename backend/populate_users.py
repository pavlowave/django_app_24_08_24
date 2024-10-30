from faker import Faker
from django.contrib.auth import get_user_model
import random
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

User = get_user_model()
fake = Faker()

roles = [role[0] for role in User.ROLES]
genders = [gender[0] for gender in User.GENDERS]
clubs = [club[0] for club in User.CLUBS]

for _ in range(100):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=65)
    phone = fake.phone_number()
    gender = random.choice(genders)
    club = random.choice(clubs)
    role = random.choice(roles)

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
        phone=phone,
        gender=gender,
        club=club,
        role=role,
        is_active=True,
        is_staff=(role == 'admin')
    )
    user.save()

print("100 пользователей успешно созданы!")
