from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from app.models import Order, OrderItem, Payment, Customer
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


@login_required
def collections_index(request):
    query = request.GET.get('q', '')
    pending_orders = Order.objects.filter(status='Pending')
    
    if query:
        pending_orders = pending_orders.filter(
            Q(customerId__user__username__icontains=query) |
            Q(customerId__user__first_name__icontains=query) |
            Q(customerId__user__last_name__icontains=query) |
            Q(customerId__user__email__icontains=query) |
            Q(customerId__phone__icontains=query) |
            Q(orderId__icontains=query)
        )
    # Get payments for verification
    for order in pending_orders:
        order.pending_payment = Payment.objects.filter(orderId=order, paymentStatus='For Verification').first()

    # Pagination
    paginator = Paginator(pending_orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'collections/collections_index.html', {
        'pending_orders': pending_orders,
        'page_obj': page_obj, 
        'query': query
        })

@login_required
def collection_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    payments = Payment.objects.filter(orderId=order)
    order_items = OrderItem.objects.filter(orderId=order)

    if request.method == 'POST':
        if 'verify' in request.POST:
            payment_id = request.POST.get('verify')
            payment = get_object_or_404(Payment, pk=payment_id)
            payment.paymentStatus = 'Completed'
            payment.processedBy = request.user
            payment.save()

            order.status = 'Under Production'
            order.save()

            send_payment_status_email(payment, 'verified')

            messages.success(request, 'Payment verified and order status updated.')
            return redirect('collection_detail', order_id=order_id)

        elif 'reject' in request.POST:
            payment_id = request.POST.get('reject')
            payment = get_object_or_404(Payment, pk=payment_id)
            payment.paymentStatus = 'Rejected'
            payment.save()

            send_payment_status_email(payment, 'rejected')

            messages.success(request, 'Payment rejected.')
            return redirect('collection_detail', order_id=order_id)

        elif 'refund' in request.POST:
            order.status = 'Pending'
            order.save()

            payment_id = request.POST.get('refund')
            payment = get_object_or_404(Payment, pk=payment_id)
            payment.paymentStatus = 'Refunded'
            payment.save()

            send_payment_status_email(payment, 'refunded')

            messages.success(request, 'Payment refunded and order status set to Pending.')
            return redirect('collection_detail', order_id=order_id)

        else:
            order.status = 'Under Production'
            order.save()

            amount = request.POST.get('amount')
            payment_method = request.POST.get('payment_method')
            payment_status = request.POST.get('payment_status')
            reference_number = request.POST.get('reference_number')

            Payment.objects.create(
                orderId=order,
                customerId=order.customerId,
                processedBy=request.user,
                amount=amount,
                paymentMethod=payment_method,
                paymentStatus=payment_status,
                referenceNumber=reference_number
            )

            messages.success(request, 'Payment added successfully.')
            return redirect('collection_detail', order_id=order_id)

    return render(request, 'collections/collection_detail.html', {'order': order, 'payments': payments, 'order_items': order_items})


def send_payment_status_email(payment, status):
    subject = f'Payment {status.capitalize()}'
    message = f'Dear {payment.customerId.user.first_name},\n\n'
    if status == 'verified':
        message += f'Your payment of ₱{payment.amount} for order #{payment.orderId.orderId} has been verified.\n\n'
        message += 'Your order is now under production.\n'
    elif status == 'rejected':
        message += f'Your payment of ₱{payment.amount} for order #{payment.orderId.orderId} has been rejected.\n\n'
        message += 'Please contact support for more information.\n'
    elif status == 'refunded':
        message += f'Your payment of ₱{payment.amount} for order #{payment.orderId.orderId} has been refunded.\n\n'
        message += 'Please contact support for more information.\n'

    message += '\nThank you for your understanding.\n\nBest regards,\nMerchTrack Team'
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [payment.customerId.user.email],
        fail_silently=False,
    )


def customer_payment(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(username=username).first()

        if user:
            customer = Customer.objects.filter(user=user).first()
            pending_orders = Order.objects.filter(customerId=customer, status='Pending')
            return render(request, 'collections/customer_payment.html', {
                'pending_orders': pending_orders,
                'customer': customer
            })
        else:
            messages.error(request, 'Username not found. Please try again.')
    
    return render(request, 'collections/customer_payment.html')

def customer_make_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        reference_number = request.POST.get('reference_number')

        Payment.objects.create(
            orderId=order,
            customerId=order.customerId,
            processedBy_id=999,
            paymentDate=now(),
            amount=amount,
            paymentMethod=payment_method,
            paymentStatus='For Verification',
            referenceNumber=reference_number
        )
        messages.success(request, 'Payment confirmation sent. Please wait for verfication.')
        return redirect('customer_payment')

    return render(request, 'collections/customer_make_payment.html', {'order': order})
