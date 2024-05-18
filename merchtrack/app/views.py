from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'index.html')

def base(request):
    return render(request, 'base.html')

def aboutUs(request):
    return render(request, 'aboutUs.html')