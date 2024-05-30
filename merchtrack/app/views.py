from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib.auth.models import User

from .forms import CreateUserForm, LoginForm, UserRegistrationForm
from .models import user_info, order_info, order_details, contact_us, Customer

def home(request):
    return render(request, 'index.html')

def success(request):
    return render(request, "success.html")

def trackOrder(request):
    try:
        student_id = request.GET.get('student_id')

        if student_id == "" or len(student_id) != 9:
            return render(request, 'index.html', {'error_message': 'ID is not valid. Please try again.'})  

        orders = order_info.objects.filter(user_info_id=student_id).values()

        if not orders:
            return render(request, 'index.html', {'error_message': 'No orders found for the provided student ID'}) 

        order_detail = order_details.objects.filter(order_details_id=orders[0]['id']).values()

        order_id = orders[0]['id']
        order_list = order_detail.all()
        total_cost = 0
        for order in order_list:
            total_cost += (float(order['item_cost']) * int(order['item_quantity']))
            print(total_cost)

        template = loader.get_template('trackOrder.html')
        context = {
            'orders': orders,
            'order_details': order_detail,
            'total_costs': total_cost,
            'order_ids': order_id
        }

        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect(request, 'index.html', {'error_message': 'An unexpected error occurred'})

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
            Customer.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                course=form.cleaned_data['course']
            )
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = UserRegistrationForm()
    return render(request, 'registration.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            print("username: " + username, "password: " + password)
            # Retrieve the user_info object with the provided student_id
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, "Invalid student ID or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        return redirect('login')

    return redirect('dashboard')

@login_required(login_url='login')
def dashboard(request):
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
            'phone': phone
        }
        
        # Store user details in the session
        request.session['user_details'] = user_details
    else:
        user_details = request.session['user_details']
        # You might need to re-fetch the user instance if you need it
        user_details['user'] = User.objects.get(id=user_details['user'])

    return render(request, 'dashboard.html', user_details)



@login_required(login_url='login')
def messages(request):
    all_messages = contact_us.objects.all().order_by('-created_at')
    return render(request, 'messages.html', {'messages': all_messages})

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