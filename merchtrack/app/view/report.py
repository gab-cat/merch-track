import os
from django.conf import settings
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
from django.contrib import messages
from django.db.models.functions import TruncDay

import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from io import BytesIO
import base64
import logging

# Set up logging
logger = logging.getLogger(__name__)

def report_index(request):
    try:
        font_path = os.path.join(settings.STATICFILES_DIRS[0], 'assets', 'montserrat.ttf')
        custom_font = fm.FontProperties(fname=font_path)

        # Update rcParams to use the custom font
        plt.rcParams['font.family'] = custom_font.get_name()
        
        # Ensure that the font is properly loaded
        fm.fontManager.addfont(font_path)
        fm._load_fontmanager(try_read_cache=False)

        # Sales data
        total_sales = Order.objects.aggregate(Sum('totalAmount'))['totalAmount__sum'] or 0
        logger.debug(f"Total sales calculated: {total_sales}")
        
        total_orders = Order.objects.count()
        logger.debug(f"Total orders counted: {total_orders}")
        
        total_items_sold = OrderItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
        logger.debug(f"Total items sold calculated: {total_items_sold}")

        # Total number of unique customers
        total_customers = Customer.objects.count()
        logger.debug(f"Total customers counted: {total_customers}")

        # Top 3 best seller items
        best_sellers = OrderItem.objects.values('productId__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:3]
        logger.debug(f"Best sellers calculated: {best_sellers}")

        # Top 3 highest revenue generating customers
        top_customers = Order.objects.values('customerId__user__last_name', 'customerId__user__first_name', 'customerId').annotate(total_spent=Sum('totalAmount')).order_by('-total_spent')[:3]
        logger.debug(f"Top customers calculated: {top_customers}")

        # Top 3 users who processed the most orders
        top_users = User.objects.annotate(processed_count=Count('processed_orders')).order_by('-processed_count')[:3]
        logger.debug(f"Top users calculated: {top_users}")

        # Collection rate
        pending_orders_amount = Order.objects.filter(status='Pending').aggregate(Sum('totalAmount'))['totalAmount__sum'] or 0
        pending_orders_count = Order.objects.filter(status='Pending').count()
        collected_amount = total_sales - pending_orders_amount
        collection_rate = (collected_amount / total_sales * 100) if total_sales > 0 else 0
        logger.debug(f"Collection rate calculated: {collection_rate}")

        # Generate sales chart
        sales_data = Order.objects.annotate(day=TruncDay('orderDate')).values('day').annotate(total=Sum('totalAmount')).order_by('day')
        days = [data['day'].strftime('%Y-%m-%d') for data in sales_data]
        sales = [data['total'] for data in sales_data]

        logger.debug(f"Sales data prepared: days={days}, sales={sales}")

        fig, ax = plt.subplots()
        ax.plot(days, sales, marker='o')
        ax.set_title('Daily Sales')
        ax.set_xlabel('Day')
        ax.set_ylabel('Sales Amount')
        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        sales_chart = base64.b64encode(image_png).decode('utf-8')

                # Monthly Revenue Growth
        monthly_revenue = (
            Order.objects.annotate(month=TruncMonth('orderDate'))
            .values('month')
            .annotate(total=Sum('totalAmount'))
            .order_by('month')
        )
        months = [data['month'].strftime('%Y-%m') for data in monthly_revenue]
        revenue = [data['total'] for data in monthly_revenue]

        # Order Status Distribution
        order_status_distribution = (
            Order.objects.values('status')
            .annotate(count=Count('status'))
        )
        statuses = [data['status'] for data in order_status_distribution]
        status_counts = [data['count'] for data in order_status_distribution]

        # Sales by Category
        sales_by_category = (
            OrderItem.objects.values('productId__category')
            .annotate(total=Sum('quantity'))
            .order_by('-total')
        )
        categories = [data['productId__category'] for data in sales_by_category]
        sales_counts = [data['total'] for data in sales_by_category]

        # Customer Retention Rate
        customer_order_counts = (
            Order.objects.values('customerId')
            .annotate(total=Count('orderId'))
            .order_by('-total')
        )
        returning_customers = len([c for c in customer_order_counts if c['total'] > 1])
        total_customers = Customer.objects.count()
        retention_rate = (returning_customers / total_customers) * 100 if total_customers > 0 else 0

        # Average Order Value (AOV)
        total_sales = Order.objects.aggregate(total=Sum('totalAmount'))['total'] or 0
        total_orders = Order.objects.count()
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0

        # Generate Monthly Revenue Growth Chart
        fig1, ax1 = plt.subplots()
        ax1.plot(months, revenue, marker='o', color='b')
        ax1.set_title('Monthly Revenue Growth')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Revenue')
        plt.xticks(rotation=45)
        plt.tight_layout()
        buffer1 = BytesIO()
        plt.savefig(buffer1, format='png')
        buffer1.seek(0)
        image_png1 = buffer1.getvalue()
        buffer1.close()
        revenue_chart = base64.b64encode(image_png1).decode('utf-8')

        # Generate Order Status Distribution Chart
        fig2, ax2 = plt.subplots()
        ax2.pie(status_counts, labels=statuses, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Order Status Distribution')
        plt.tight_layout()
        buffer2 = BytesIO()
        plt.savefig(buffer2, format='png')
        buffer2.seek(0)
        image_png2 = buffer2.getvalue()
        buffer2.close()
        status_chart = base64.b64encode(image_png2).decode('utf-8')

        # Generate Sales by Category Chart
        fig3, ax3 = plt.subplots()
        ax3.bar(categories, sales_counts, color='g')
        ax3.set_title('Sales by Category')
        ax3.set_xlabel('Category')
        ax3.set_ylabel('Sales Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        buffer3 = BytesIO()
        plt.savefig(buffer3, format='png')
        buffer3.seek(0)
        image_png3 = buffer3.getvalue()
        buffer3.close()
        category_chart = base64.b64encode(image_png3).decode('utf-8')


        messages.info(request, "Welcome to Insightify v1.0.1")
        return render(request, 'reports/report_index.html', {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'total_items_sold': total_items_sold,
            'total_customers': total_customers,
            'best_sellers': best_sellers,
            'top_customers': top_customers,
            'top_users': top_users,
            'collection_rate': collection_rate,
            'pending_orders_amount': pending_orders_amount,
            'pending_orders_count': pending_orders_count,
            'collected_amount': collected_amount,
            'sales_chart': sales_chart,
            'revenue_chart': revenue_chart,
            'status_chart': status_chart,
            'category_chart': category_chart,
            'retention_rate': retention_rate,
            'avg_order_value': avg_order_value,
            'returning_customers': returning_customers,
            'total_customers': total_customers,
        })
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def order_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        orders = Order.objects.filter(orderDate__range=[start_date, end_date])
    else:
        orders = Order.objects.all()
    
    if request.GET.get('export') == 'excel':
        return or_export_to_excel(orders)

    return render(request, 'reports/order_report.html', {'orders': orders})

def or_export_to_excel(orders):
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
    response['Content-Disposition'] = 'attachment; filename=order_report.xlsx'
    wb.save(response)
    
    return response

def product_report(request, product_id=None):
    status = request.GET.get('status')
    products = Product.objects.all()
    order_statuses = ['Pending', 'Under Production', 'Completed']

    selected_product_name=""
    
    if product_id:
        orders = Order.objects.filter(orderitem__productId=product_id)
        if status:
            orders = orders.filter(status=status)
        orders = orders.distinct()
        total_quantity = OrderItem.objects.filter(productId=product_id).aggregate(Sum('quantity'))['quantity__sum'] or 0

                # Get the selected product's name
        selected_product = Product.objects.filter(productId=product_id).first()
        if selected_product:
            selected_product_name = selected_product.name

    else:
        orders = Order.objects.none()
        total_quantity = 0

    if request.GET.get('export') == 'excel':
        return pr_export_to_excel(orders)

    return render(request, 'reports/product_report.html', {
        'orders': orders,
        'total_quantity': total_quantity,
        'products': products,
        'selected_product_id': product_id,
        'selected_product_name': selected_product_name,
        'status': status,
        'order_statuses': order_statuses,
    })

def pr_export_to_excel(orders):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orders"

    headers = ['Order ID', 'Customer', 'Date', 'Email', 'Phone', 'Quantity', 'Status', 'Size', 'Note']
    ws.append(headers)

    for order in orders:
        for item in order.orderitem_set.all():
            ws.append([
                order.orderId,
                f"{order.customerId.user.first_name} {order.customerId.user.first_name}",
                make_naive(order.orderDate),  # Convert to naive datetime
                order.customerId.user.email,
                order.customerId.phone,
                item.quantity,
                order.status,
                item.size,
                item.customerNote
            ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=product_report.xlsx'
    wb.save(response)
    
    return response

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
    start_date = request.GET.get('start_date', timezone.now().replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))

    orders = Order.objects.filter(orderDate__range=[start_date, end_date])
    total_sales = orders.aggregate(total_sales=Sum('totalAmount'))['total_sales'] or 0
    total_discount = orders.aggregate(total_discount=Sum('discountAmount'))['total_discount'] or 0
    total_orders = orders.count()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0

    if request.GET.get('export') == 'excel':
        return sr_export_to_excel(orders, total_sales, total_discount, total_orders, avg_order_value, start_date, end_date)

    return render(request, 'reports/sales_report.html', {
        'orders': orders,
        'total_sales': total_sales,
        'total_discount': total_discount,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'start_date': start_date,
        'end_date': end_date,
    })

def sr_export_to_excel(orders, total_sales, total_discount, total_orders, avg_order_value, start_date, end_date):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    headers = ['Order ID', 'Customer', 'Date', 'Status', 'Total Amount', 'Discount Amount']
    ws.append(headers)

    for order in orders:
        ws.append([
            order.orderId,
            order.customerId.user.username,
            make_naive(order.orderDate),  # Convert to naive datetime
            order.status,
            order.totalAmount,
            order.discountAmount
        ])

    # Summary row
    ws.append([])
    ws.append(['Total Sales', total_sales])
    ws.append(['Total Discount', total_discount])
    ws.append(['Total Orders', total_orders])
    ws.append(['Average Order Value', avg_order_value])
    ws.append(['Start Date', start_date])
    ws.append(['End Date', end_date])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    wb.save(response)
    
    return response

def fulfillment_report(request):
    orders = Order.objects.all()
    on_time_delivery = orders.filter(estimatedDeliveryDate__gte=F('orderitem__deliveryDate')).count()
    late_delivery = orders.filter(estimatedDeliveryDate__lt=F('orderitem__deliveryDate')).count()
    return render(request, 'reports/fulfillment_report.html', {'on_time_delivery': on_time_delivery, 'late_delivery': late_delivery})