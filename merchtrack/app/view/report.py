from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from app.models import Customer, Order, OrderItem, Product
from app.forms import CustomerForm
from django.db.models import Sum, Count
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import F
import openpyxl
from django.http import HttpResponse
from django.utils.timezone import make_naive


def order_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        orders = Order.objects.filter(orderDate__range=[start_date, end_date])
    else:
        orders = Order.objects.all()
    return render(request, 'reports/order_report.html', {'orders': orders})

def product_report(request, product_id=None):
    status = request.GET.get('status')
    products = Product.objects.all()
    order_statuses = ['Pending', 'Under Production', 'Completed']
    
    if product_id:
        orders = Order.objects.filter(orderitem__productId=product_id)
        if status:
            orders = orders.filter(status=status)
        orders = orders.distinct()
        total_quantity = OrderItem.objects.filter(productId=product_id).aggregate(Sum('quantity'))['quantity__sum'] or 0
    else:
        orders = Order.objects.none()
        total_quantity = 0

    return render(request, 'reports/product_report.html', {
        'orders': orders,
        'total_quantity': total_quantity,
        'products': products,
        'selected_product_id': product_id,
        'status': status,
        'order_statuses': order_statuses,
    })
def sales_data_api(request, product_id):
    sales_over_time = (
        OrderItem.objects.filter(productId=product_id)
        .values('orderId__orderDate')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('orderId__orderDate')
    )
    quantity_by_customer = (
        OrderItem.objects.filter(productId=product_id)
        .values('orderId__customerId__user__username')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')
    )
    data = {
        'sales_over_time': list(sales_over_time),
        'quantity_by_customer': list(quantity_by_customer)
    }
    return JsonResponse(data)

def customer_report(request):
    customer_id = request.GET.get('customer_id')
    status = request.GET.get('status')
    customers = Customer.objects.all()
    order_statuses = ['Pending', 'Under Production', 'Completed']
    
    if customer_id:
        orders = Order.objects.filter(customerId=customer_id)
        if status:
            orders = orders.filter(status=status)
        orders = orders.distinct()
        total_spending = orders.aggregate(Sum('totalAmount'))['totalAmount__sum'] or 0
    else:
        orders = Order.objects.none()
        total_spending = 0

    if request.GET.get('export') == 'excel':
        return export_to_excel(orders)

    return render(request, 'reports/customer_report.html', {
        'orders': orders,
        'total_spending': total_spending,
        'customers': customers,
        'selected_customer_id': customer_id,
        'status': status,
        'order_statuses': order_statuses,
    })

def export_to_excel(orders):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orders"

    headers = ['Order ID', 'Customer', 'Date', 'Status', 'Total Amount']
    ws.append(headers)

    for order in orders:
        ws.append([
            order.orderId,
            order.customerId.user.username,
            make_naive(order.orderDate),  # Convert to naive datetime
            order.status,
            order.totalAmount
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=customer_report.xlsx'
    wb.save(response)
    return response

def sales_report(request):
    start_date = request.GET.get('start_date', timezone.now().replace(day=1))
    end_date = request.GET.get('end_date', timezone.now())
    orders = Order.objects.filter(orderDate__range=[start_date, end_date])
    total_sales = orders.aggregate(total_sales=Sum('totalAmount'))['total_sales']
    return render(request, 'reports/sales_report.html', {'orders': orders, 'total_sales': total_sales})

def fulfillment_report(request):
    orders = Order.objects.all()
    on_time_delivery = orders.filter(estimatedDeliveryDate__gte=F('orderitem__deliveryDate')).count()
    late_delivery = orders.filter(estimatedDeliveryDate__lt=F('orderitem__deliveryDate')).count()
    return render(request, 'reports/fulfillment_report.html', {'on_time_delivery': on_time_delivery, 'late_delivery': late_delivery})