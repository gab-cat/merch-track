from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.timezone import now
from app.models import Order, Fulfillment, OrderItem, Product, User
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives

@login_required
def fulfillment_view(request):
    query = request.GET.get('q', '')
    item_query = request.GET.get('item_q', '')
    products = Product.objects.all()
    
    under_production_orders = Order.objects.filter(status='Under Production')
    ready_orders = Order.objects.filter(status='Ready')

    if query:
        under_production_orders = under_production_orders.filter(
            Q(customerId__user__username__icontains=query) |
            Q(customerId__user__email__icontains=query) |
            Q(customerId__user__first_name__icontains=query) |
            Q(customerId__user__last_name__icontains=query) |
            Q(orderId__icontains=query)
        )
        ready_orders = ready_orders.filter(
            Q(customerId__user__username__icontains=query) |
            Q(customerId__user__email__icontains=query) |
            Q(customerId__user__first_name__icontains=query) |
            Q(customerId__user__last_name__icontains=query) |
            Q(orderId__icontains=query)
        )

    if item_query:
        under_production_orders = under_production_orders.filter(
            orderitem__productId__name__icontains=item_query
        ).distinct()
        ready_orders = ready_orders.filter(
            orderitem__productId__name__icontains=item_query
        ).distinct()

    if request.method == 'POST':
        if 'mark_ready' in request.POST:
            order_id = request.POST.get('mark_ready')
            order = get_object_or_404(Order, pk=order_id)
            order.status = 'Ready'
            order.save()
            send_order_email(order, 'ready', request)
            messages.success(request, f'Order #{order_id} marked as ready.')
        elif 'mark_completed' in request.POST:
            order_id = request.POST.get('mark_completed')
            order = get_object_or_404(Order, pk=order_id)
            fulfillment_date = now()
            order.status = 'Completed'
            order.save()

            # Determine if the order is On Time or Late
            status = 'On Time' if fulfillment_date.date() <= order.estimatedDeliveryDate.date() else 'Late'
            Fulfillment.objects.create(orderId=order, processedBy=request.user, status=status, fulfillmentDate=fulfillment_date)

            send_order_email(order, 'completed', request)
            messages.success(request, f'Order #{order_id} marked as {status.lower()}.')

        return redirect('fulfillment_view')

    return render(request, 'fulfillment/order_fulfillment.html', {
        'under_production_orders': under_production_orders,
        'ready_orders': ready_orders,
        'query': query,
        'item_query': item_query,
        'products': products,
    })

def send_order_email(order, email_type, request):
    customer = order.customerId.user
    subject = ""
    if email_type == "ready":
        subject = "Your Order is Ready for Pickup"
        template_name = "emails/order_ready.html"
    elif email_type == "completed":
        subject = "Thank You for Your Purchase"
        template_name = "emails/order_completed.html"
    
    from_email = "Merch Track Team <no-reply@merchtrack.com>"
    context = {
        'order': order,
        'email': customer.email,
        'domain': 'yourdomain.com',  # Replace with your actual domain or use request.get_host()
        'site_name': 'Merch Track',
        'username': customer.username,
        'fullname': f"{customer.first_name} {customer.last_name}",
        'survey_link': f"http://{request.get_host()}/survey/{order.orderId}/"
    }
    
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, from_email, [customer.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
