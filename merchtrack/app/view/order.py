import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from app.models import Customer, Product, Order, OrderItem
from app.form.order import OrderForm, OrderItemForm
from django.core.paginator import Paginator
from django.contrib import messages as django_messages

@login_required
def create_order(request):
    products = Product.objects.filter(available=True)
    customers = Customer.objects.all()
    order_form = OrderForm(request.POST)

    if request.method == 'POST':
        customer_id = request.POST.get('customerId')
        total_amount = request.POST.get('totalAmount')
        discount_amount = request.POST.get('discountAmount')
        estimated_delivery_date = request.POST.get('estimatedDeliveryDate')
        processed_by = request.user

        if not customer_id or not total_amount or not estimated_delivery_date:
            # Handle missing data
            django_messages.error(request, "Please fill in all required fields.")
            return render(request, 'create_order.html', {
                'order_form': order_form,
                'products': products,
                'customers': customers,
                'error_message': 'Please fill in all required fields.'
            })

        # Create the Order object
        order = Order(
            customerId_id=customer_id,
            totalAmount=total_amount,
            discountAmount=discount_amount,
            estimatedDeliveryDate=estimated_delivery_date,
            processedBy=processed_by
        )
        order.save()

        # Save order items
        for item in request.POST.getlist('items'):
            item_data = json.loads(item)
            order_item = OrderItem(
                orderId=order,
                productId_id=item_data['productId'],
                quantity=item_data['quantity'],
                price=item_data['price'],
                customerNote=item_data.get('note', ''),
                size=item_data.get('size', '') ,
            )
            order_item.save()
        django_messages.success(request, "Successfully created a new order.")
        return redirect('success')  # Redirect to a success page

    return render(request, 'create_order.html', {
        'products': products,
        'customers': customers,
        'order_form': order_form,
    })

def order_list(request):
    orders = Order.objects.all().order_by('-orderDate')
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'orders/order_list.html', {'page_obj': page_obj})

def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})

def edit_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            django_messages.success(request, f"Successfully updated order with ID: {order_id}")
            return redirect('order_detail', order_id=order.orderId)
        else:
            django_messages.error(request, "Something went wrong. Unable to complete your request.")
    else:
        
        form = OrderForm(instance=order)

    return render(request, 'orders/edit_order.html', {'form': form, 'order': order})

def delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.delete()
        django_messages.success(request, "Successfully deleted an order.")
        return redirect('order_list')
    return render(request, 'orders/confirm_delete.html', {'order': order})

def sales_report(request):
    sales = Order.objects.filter(status='Completed').aggregate(total_sales=sum('totalAmount'))
    return render(request, 'orders/sales_report.html', {'sales': sales})
