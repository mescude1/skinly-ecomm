#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skinly_core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@skinly.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print("Superuser 'admin' created successfully!")
    print("Username: admin")
    print("Password: admin123")
    print("Email: admin@skinly.com")
else:
    print("Superuser 'admin' already exists!")