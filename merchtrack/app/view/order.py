import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from app.models import Customer, Product, Order, OrderItem
from app.form.order import OrderForm, OrderItemForm

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

        return render(request, 'success.html')  # Redirect to a success page

    return render(request, 'create_order.html', {
        'products': products,
        'customers': customers,
        'order_form': order_form,
    })


