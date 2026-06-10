from django.shortcuts import redirect
from django.urls import reverse
from .models import UserProfile

class ProfileRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
