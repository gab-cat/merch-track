from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import CreateUserForm, LoginForm
from .models import user_info, order_info, order_details, contact_us
def home(request):
    return render(request, 'index.html')

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
    cursor.execute('select app_order_info.order_details_id, app_user_info.student_id, app_user_info.student_name, app_order_info.payment_method, app_order_info.payment_status, app_order_info.order_status from app_order_info join app_user_info on app_order_info.user_info_ID = app_user_info.student_id')
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

@login_required(login_url='login')
def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CreateUserForm()
    
    context = {'form': form}
    return render(request, 'registration.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['username']
            password = form.cleaned_data['password']

            print("username: " + student_id, "password: " + password)
            # Retrieve the user_info object with the provided student_id
            try:
                user_info_obj = user_info.objects.get(student_id=student_id)
            except user_info.DoesNotExist:
                user_info_obj = None

            if user_info_obj:
                # Authenticate using the user_info's associated User object
                user = authenticate(request, username=user_info_obj.user.username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('dashboard')
                else:
                    form.add_error(None, "Invalid student ID or password.")
            else:
                form.add_error(None, "Invalid student ID or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    # Access user details
    user = request.user

    user_info_obj = user_info.objects.get(student_id=user)
    student_name = user_info_obj.student_name
    course = user_info_obj.course
    email = user_info_obj.email

    
    context = {
        'user': user,
        'student_id': user,
        'student_name': student_name,
        'course': course,
        'email': email,
        # Add other user details as needed
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def messages(request):
    all_messages = contact_us.objects.all().order_by('-created_at')
    return render(request, 'messages.html', {'messages': all_messages})

    