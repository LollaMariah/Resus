from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from .forms import RegistrationForm
from .models import User
from .neomodel_models import NeoUser

class SignUpView(generic.CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('registration_complete')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        NeoUser(email=user.email, is_active=True, is_admin=user.is_admin).save()
        return super().form_valid(form)

def kursus_card(request):
    return render(request, 'kursus/kursus.html')

def pilih_role(request):
    context = {
        'range': range(1, 21)  # Adjust the range as needed
    }
    return render(request, 'kursus/pilih_role.html', context)

def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'kursus/index.html')

def login(request):
    return render(request, 'kursus/login.html')

def registrasi(request):
    return render(request, 'kursus/registrasi.html')

def detail_kursus(request):
    return render(request, 'kursus/detail_kursus.html')

