import os
import django

def create_superuser():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    username = 'ankitadmin'
    email = 'ankitadmin@example.com'
    password = 'Ankit@12345'
    
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser {username}...")
        User.objects.create_superuser(username, email, password)
        print(f"Superuser {username} created successfully.")
    else:
        print(f"Superuser {username} already exists.")

if __name__ == "__main__":
    create_superuser()
