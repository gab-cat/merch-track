from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from app.form.product import ProductForm
from app.models import Product

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            print("Product image path:", product.productImage.url if product.productImage else "No image uploaded")
            return redirect('dashboard')  # Redirect to the dashboard or another page after successful form submission
        else:
            print("Form is invalid")
            print("Errors:", form.errors)
    else:
        form = ProductForm()
    
    return render(request, 'create_product.html', {'form': form})
