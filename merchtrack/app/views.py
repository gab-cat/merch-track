from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def trackOrder(request):
    return render(request, 'trackOrder.html')

def aboutUs(request):
    return render(request, 'aboutUs.html')

def contactUs(request):
    return render(request, 'contactUs.html')
