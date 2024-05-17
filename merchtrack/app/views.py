from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def not_found(request):
    return render(request, '404.html', status=404)
    
def trackOrder(request):
    return render(request, 'trackOrder.html')

def aboutUs(request):
    return render(request, 'aboutUs.html')

def contactUs(request):
    return render(request, 'contactUs.html')

def adminTracker(request):
    return render(request, 'adminTracker.html')
