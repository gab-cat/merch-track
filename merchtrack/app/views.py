from django.contrib.auth.models import Group
import logging
from django.conf import settings
from django.contrib import messages as django_messages

from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from app.auth import group_required

from .forms import CreateUserForm, CustomerSatisfactionSurveyForm, LoginForm, UserRegistrationForm
from .models import  CustomerSatisfactionSurvey, Order, user_info, order_info, order_details, contact_us, Customer

from .utils import log_action
from django.core.mail import send_mail


# Set up logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'index.html')

def success(request):
    return render(request, "success.html")

# def trackOrder(request):
#     try:
#         student_id = request.GET.get('student_id')

#         if student_id == "" or len(student_id) != 9:
#             return render(request, 'index.html', {'error_message': 'ID is not valid. Please try again.'})  

#         orders = order_info.objects.filter(user_info_id=student_id).values()

#         if not orders:
#             return render(request, 'index.html', {'error_message': 'No orders found for the provided student ID'}) 

#         order_detail = order_details.objects.filter(order_details_id=orders[0]['id']).values()

#         order_id = orders[0]['id']
#         order_list = order_detail.all()
#         total_cost = 0
#         for order in order_list:
#             total_cost += (float(order['item_cost']) * int(order['item_quantity']))
#             print(total_cost)

#         template = loader.get_template('trackOrder.html')
#         context = {
#             'orders': orders,
#             'order_details': order_detail,
#             'total_costs': total_cost,
#             'order_ids': order_id
#         }

#         return HttpResponse(template.render(context, request))
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return redirect(request, 'index.html', {'error_message': 'An unexpected error occurred'})

def aboutUs(request):
    return render(request, "aboutUs.html")

def contactUs(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        new_contact = contact_us.objects.create(name=name,email=email,message=message)
        new_contact.save()
        return render(request, "contactUs.html", {'success_message': 'Message was sent successfully to our team. Kindly give us 2-3 business days, and we\'ll be right with you. Thank you for contacting us!'}) 
    else:  
        return render(request, "contactUs.html")

def not_found(request):
    return render(request, '404.html', status=404)

@login_required(login_url='login')
def adminTracker(request):
    cursor = connection.cursor()
    cursor.execute('select app_order_info.order_details_id, app_user_info.student_id, app_user_info.student_name, app_user_info.email, app_user_info.course, app_order_info.payment_method, app_order_info.payment_status, app_order_info.order_status from app_order_info join app_user_info on app_order_info.user_info_ID = app_user_info.student_id')
    results = cursor.fetchall()
    print(results)
    return render(request, 'adminTracker.html', {'orders' : results})

@login_required(login_url='login')
def orderEntry(request):
    if request.method == 'POST':
        # Extracting order details data
        student_id = request.POST.get('student_id')
        item_name = request.POST.get('item_name')
        item_size = request.POST.get('item_size')
        item_color = request.POST.get('item_color')
        item_cost = request.POST.get('item_cost')
        item_quantity = request.POST.get('item_quantity')

        order_date = request.POST.get('order_date')
        distribution_date = request.POST.get('distribution_date')
        payment_method = request.POST.get('payment_method')

        order_details_instance = order_details(
            item_name=item_name,
            item_size=item_size,
            item_color=item_color,
            item_cost=item_cost,
            item_quantity=item_quantity
        )
        order_details_instance.save()

        order_info_instance = order_info(
            order_date=order_date,
            distribution_date=distribution_date,
            order_status="Pending",
            payment_method=payment_method,
            payment_status="Not yet Paid",
            order_details_id=order_details_instance.id,
            user_info_id=student_id
        )
        order_info_instance.save()

        return render(request, "success.html")

    return render(request, "order-entry.html")

def studentInfo(request):
    student_id = request.GET.get('student_id')
    
    if not student_id:
        return HttpResponse("Student ID not provided", status=400)

    try:
        student = get_object_or_404(user_info, student_id=student_id)
        student_data = {
            'student_id': student.student_id,
            'student_name': student.student_name,
            'email': student.email,
            'course': student.course,
        }
        return JsonResponse(student_data)
    except user_info.DoesNotExist:
        return HttpResponse("Student not found", status=404)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Create a Customer instance
            customer_group = Group.objects.get(name='Customers')
            user.groups.add(customer_group)

            customer = Customer.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                course=form.cleaned_data['course']
            )
            log_action(user, 'User Registration', f'User {user.username} registered.', customer)
            django_messages.success(request, "Account successfully created.")
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = UserRegistrationForm()
    return render(request, 'registration.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error = 0

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff:
                    auth_login(request, user)# Log the type of messages
                    django_messages.info(request, 'Logged in successfully.')
                    return redirect('dashboard')
                else:
                    django_messages.error(request, "You are not authorized to access this page.")
                    return redirect('login')
        else:
            django_messages.error(request, "Invalid username or password.")
    else:
        if error == 1:
            django_messages.error(request, "Invalid username or password.")
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required(login_url='login')
def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        django_messages.info(request, 'Logged out successfully.')
        return redirect('login')
    
    django_messages.error(request, 'Something went wrong.')
    return redirect('dashboard')

@login_required(login_url='login')
def dashboard(request):
    groups = request.user.groups.all()
    if 'user_details' not in request.session:
        user = request.user
        student_name = f"{user.first_name} {user.last_name}"
        email = user.email

        try:
            customer = Customer.objects.get(user=user)
            course = customer.course
            phone = customer.phone
        except Customer.DoesNotExist:
            course = None
            phone = None
        
        user_details = {
            'user': user.id,
            'student_id': user.id,
            'student_name': student_name,
            'course': course,
            'email': email,
            'phone': phone,
        }
        
        # Store user details in the session
        request.session['user_details'] = user_details
    else:
        user_details = request.session['user_details']
        # You might need to re-fetch the user instance if you need it
        user_details['user'] = User.objects.get(id=user_details['user'])

    return render(request, 'dashboard.html', {
        'user_details': user_details,
        'groups': groups,
    })



@login_required(login_url='login')
@group_required('Staffs')
def cust_messages(request):
    all_messages = contact_us.objects.all().order_by('-created_at')
    return render(request, 'messages.html', {'cust_messages': all_messages})

@login_required(login_url='login')
@group_required('Staffs')
def send_reply_email(request):
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')
        reply_message = request.POST.get('reply_message')
        if recipient_email and reply_message:
            subject = "Reply to Your Message"
            message = reply_message
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [recipient_email]

            send_mail(subject, message, from_email, recipient_list)
            django_messages.success(request, 'Reply sent successfully.')
        else:
            django_messages.error(request, 'Failed to send reply. Please make sure all fields are filled.')
    return redirect('messages')

@login_required(login_url='login')
@group_required('Staffs')
def customer_info(request):
    email = request.GET.get('email')
    try:
        user = User.objects.get(email=email)
        customer = Customer.objects.get(user=user)
        data = {
            'valid': True,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': customer.phone,
            'course': customer.course,
            "id": customer.user_id
        }

    except User.DoesNotExist:
        data = {'valid': False}
    return JsonResponse(data)

def survey_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status="Completed")
    existing_survey = CustomerSatisfactionSurvey.objects.filter(order=order).first()

    if existing_survey:
        return render(request, 'survey/survey_already_filled.html')

    if request.method == 'POST':
        form = CustomerSatisfactionSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.order = order
            survey.save()
            log_action(request.user, 'Survey Completed', f'Customer {request.user.username} completed survey for Order {order_id}.', order.customerId)
            django_messages.success(request, 'Thank you for completing the survey!')
            return redirect('survey_thank_you')  # Redirect to an appropriate page
    else:
        form = CustomerSatisfactionSurveyForm()

    return render(request, 'survey/survey_form.html', {'form': form, 'order': order})

def survey_thank_you(request):
    return render(request, 'survey/survey_thank_you.html')