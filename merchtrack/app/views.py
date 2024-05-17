from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import user_info, order_info, order_details

def home(request):
    return render(request, 'index.html')

def trackOrder(request):
    try:
        print("(console.log) Updated")
        student_id = request.GET.get('student_id')

        # order_details_id = request.GET.get('order_details_ID')

        # order_info.objects.filter(order_details_ID=order_details_id).values()

        order_deets = order_info.objects.all().values()
        print(order_deets)
        
        orders = order_info.objects.filter(user_info_ID=student_id).values()

        order_detail = order_details.objects.filter(order_details_ID=orders[0]['id']).values() #
        
        template = loader.get_template('trackOrder.html')
        context = {
            'orders': orders,
            'order_details': order_detail,
        }
        
        return HttpResponse(template.render(context, request))
    except user_info.DoesNotExist:
        student = None
        
        return render(request, "index.html", {'error_message': 'student id does not exist'})

def not_found(request):
    return render(request, '404.html', status=404)

def aboutUs(request):
    return render(request, 'aboutUs.html')

def contactUs(request):
    return render(request, 'contactUs.html')

def adminTracker(request):
    return render(request, 'adminTracker.html')
