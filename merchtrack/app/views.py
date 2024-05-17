from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def not_found(request):
    return render(request, '404.html', status=404)