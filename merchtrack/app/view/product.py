from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from app.form.product import ProductForm
from app.models import Customer, Product
from django.contrib import messages

from app.utils import log_action
from app.auth import group_required


customer = Customer.objects.get(pk=999)


@login_required(login_url='login')
@group_required('Product')
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            log_action(request.user, 'Product Created', f"Product {product.name} (ID: {product.productId}) created by {request.user.username}.", customer)
            messages.success(request, "Successfully created a product.")
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'products/create_product.html', {'form': form})

@login_required(login_url='login')
def product_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(name__icontains=query)
    
    if category:
        products = products.filter(category=category)
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
    })

@login_required(login_url='login')
@group_required('Product')
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            if form.has_changed():
                changes = []
                for field in form.changed_data:
                    old_value = getattr(product, field)
                    new_value = form.cleaned_data[field]
                    changes.append(f"{field} changed from '{old_value}' to '{new_value}'")

                form.save()
                change_details = "\n".join(changes)
                log_action(request.user, 'Product Edited', f"Product {product.name} (ID: {product.productId}) edited by {request.user.username}.\n{change_details}", customer)
                messages.success(request, f"Successfully updated product with ID: {product_id}.")
                return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product,
        'categories': categories
    })

@login_required(login_url='login')
@group_required('Product')
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        log_action(request.user, 'Product Deleted', f"Product {product.name} (ID: {product.productId}) deleted by {request.user.username}.", customer)
        product.delete()
        messages.success(request, f"Successfully deleted product with ID : {product_id}")
        return redirect('product_list')
    return render(request, 'products/confirm_delete.html', {'product': product})