import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from app.models import Customer, Product, Order, OrderItem
from app.form.order import OrderForm, OrderItemForm
from django.core.paginator import Paginator
from django.contrib import messages as django_messages
from django.db.models import Q

from app.utils import log_action
from app.auth import group_required

@login_required(login_url='login')
@group_required('Order-Entry')
def create_order(request):
    products = Product.objects.filter(available=True)
    for product in products:
        product.direct_image_link = product.get_image()
    customers = Customer.objects.all()
    order_form = OrderForm(request.POST)

    if request.method == 'POST':
        customer_id = request.POST.get('customerId')
        total_amount = request.POST.get('totalAmount')
        discount_amount = request.POST.get('discountAmount')
        estimated_delivery_date = request.POST.get('estimatedDeliveryDate')
        processed_by = request.user

        if not customer_id or not total_amount or not estimated_delivery_date:
            django_messages.error(request, "Please fill in all required fields.")
            return render(request, 'create_order.html', {
                'order_form': order_form,
                'products': products,
                'customers': customers,
                'error_message': 'Please fill in all required fields.'
            })

        order = Order(
            customerId_id=customer_id,
            totalAmount=total_amount,
            discountAmount=discount_amount,
            estimatedDeliveryDate=estimated_delivery_date,
            processedBy=processed_by
        )
        order.save()

        for item in request.POST.getlist('items'):
            item_data = json.loads(item)
            order_item = OrderItem(
                orderId=order,
                productId_id=item_data['productId'],
                quantity=item_data['quantity'],
                price=item_data['price'],
                customerNote=item_data.get('note', ''),
                size=item_data.get('size', '')
            )
            order_item.save()

        log_action(request.user, 'Order Created', f"Order {order.orderId} created by {request.user.username}.", order.customerId)
        django_messages.success(request, f"Successfully created a new order with ID: {order.orderId}.")
        return redirect('success')

    return render(request, 'create_order.html', {
        'products': products,
        'customers': customers,
        'order_form': order_form,
    })


@login_required(login_url='login')
def order_list(request):
    query = request.GET.get('q')
    status = request.GET.get('status')

    orders = Order.objects.all().order_by('-orderDate')

    if status:
        orders = orders.filter(status=status)

    if query:
        orders = orders.filter(
            Q(orderId__icontains=query) |
            Q(customerId__user__first_name__icontains=query) |
            Q(customerId__user__last_name__icontains=query)
        )

    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'status': status,
    }

    return render(request, 'orders/order_list.html', context)

def order_detail(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        django_messages.error(request, "Order ID is not found. Please try again.")
        return redirect('home')
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required(login_url='login')
@group_required('Order-Entry')
def edit_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            if form.has_changed():
                changes = []
                for field in form.changed_data:
                    old_value = getattr(order, field)
                    new_value = form.cleaned_data[field]
                    changes.append(f"{field} changed from '{old_value}' to '{new_value}'")

                form.save()
                change_details = "\n".join(changes)
                log_action(request.user, 'Order Edited', f"Order {order.orderId} edited by {request.user.username}.\n{change_details}", order.customerId)
                django_messages.success(request, f"Successfully updated order with ID: {order_id}.")
                return redirect('order_detail', order_id=order.orderId)
        else:
            django_messages.error(request, "Something went wrong. Unable to complete your request.")
    else:
        form = OrderForm(instance=order)

    return render(request, 'orders/edit_order.html', {'form': form, 'order': order})


@login_required(login_url='login')
@group_required('Order-Entry')
def delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        log_action(request.user, 'Order Deleted', f"Order {order.orderId} deleted by {request.user.username}.", order.customerId)
        order.delete()
        django_messages.success(request, f"Successfully deleted order with ID : {order_id}")
        return redirect('order_list')
    return render(request, 'orders/confirm_delete.html', {'order': order})

def sales_report(request):
    sales = Order.objects.filter(status='Completed').aggregate(total_sales=sum('totalAmount'))
    return render(request, 'orders/sales_report.html', {'sales': sales})
