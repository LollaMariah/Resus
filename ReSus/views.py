from django.shortcuts import render

def kursus_card(request):
    # Konten fungsi book_list
    return render(request, 'kursus/kursus.html')

def home(request):
    # Konten fungsi home
    return render(request, 'home.html')

def index(request):
    # Konten fungsi home
    return render(request, 'kursus/index.html')

def login(request):
    # Konten fungsi book_list
    return render(request, 'kursus/login.html')

def registrasi(request):
    # Konten fungsi book_list
    return render(request, 'kursus/registrasi.html')
