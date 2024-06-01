from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from app.form.product import ProductForm
from app.models import Product
from django.contrib import messages

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'create_product.html', {'form': form})

def product_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(name__icontains=query)
    
    if category:
        products = products.filter(category=category)
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
    })

def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully updated a product.")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    # Query all distinct categories
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    return render(request, 'edit_product.html', {
        'form': form,
        'product': product,
        'categories': categories
    })


def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'confirm_delete.html', {'product': product})