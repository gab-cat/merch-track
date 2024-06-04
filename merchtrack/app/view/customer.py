from django.shortcuts import render, get_object_or_404, redirect
from app.models import Customer, Order
from app.forms import CustomerForm, UserForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required(login_url='login')
def customer_list(request):
    query = request.GET.get('q')
    is_staff = request.GET.get('is_staff')
    is_active = request.GET.get('is_active')

    customer_list = Customer.objects.all()

    if is_staff:
        customer_list = customer_list.filter(user__is_staff=is_staff == 'true')

    if is_active:
        customer_list = customer_list.filter(user__is_active=is_active == 'true')

    if query:
        customer_list = customer_list.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(phone__icontains=query)
        )

    paginator = Paginator(customer_list, 10)  # Show 10 customers per page.
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)

    if query == "None":
        query = ""

    context = {
        'customers': customers,
        'query': query,
        'is_staff': is_staff,
        'is_active': is_active,
    }

    return render(request, 'customers/customer_list.html', context)

@login_required(login_url='login')
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    orders = Order.objects.filter(customerId=customer)
    return render(request, 'customers/customer_detail.html', {'customer': customer, 'orders': orders})

def send_html_password_reset_email(user, request):
    subject = "Reset Your Password"
    from_email = f"Merch Track Help Desk Team"
    context = {
        'email': user.email,
        'domain': request.get_host(),
        'site_name': 'Merch Track',
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'username': user.username,
        'fullname': f"{user.first_name} {user.last_name}"
    }
    html_content = render_to_string('registration/password_reset_email.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()

@login_required(login_url='login')
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    user = customer.user
    if request.method == 'POST':
        if 'reset_password' in request.POST:
            password_reset_form = PasswordResetForm({'email': user.email})
            if password_reset_form.is_valid():
                send_html_password_reset_email(user, request)
                messages.success(request, "Password reset link successfully sent.")
                return redirect('customer_detail', customer_id=customer.user_id)
        else:
            customer_form = CustomerForm(request.POST, instance=customer)
            user_form = UserForm(request.POST, instance=user)
            if customer_form.is_valid() and user_form.is_valid():
                user_form.save()
                customer_form.save()
                messages.success(request, "Changes saved successfully.")
                return redirect('customer_detail', customer_id=customer.user_id)
    else:
        customer_form = CustomerForm(instance=customer)
        user_form = UserForm(instance=user)
    return render(request, 'customers/edit_customer.html', {'customer_form': customer_form, 'user_form': user_form, 'customer': customer})

@login_required(login_url='login')
def send_password_reset_email(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    password_reset_form = PasswordResetForm({'email': user.email})
    if password_reset_form.is_valid():
        request = request._request
        opts = {
            'use_https': request.is_secure(),
            'token_generator': default_token_generator,
            'from_email': None,
            'request': request,
        }
        password_reset_form.save(**opts)
        return redirect('customer_detail', customer_id=user.customer.user_id)
