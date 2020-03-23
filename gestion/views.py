from django.shortcuts import render
# ... other import statements ...
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import FaseForm


def index(request):
    user = request.user
    return render(request, 'index.html')
    if user.is_authenticated:
        return redirect(perfil)
    else:
        return render(request, 'index.html')


# ... index, profile ...


@login_required
def perfil(request):
    user = request.user
    print(user)
    print("aqui no hay error")
    auth0user = user.social_auth.filter(provider='auth0')[0]
    #usuario=User.objects.get(username=request.user.username)
    #print(user.email_addess)

    print("aqui tampoco")
    print(auth0user.extra_data)
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture'],
        #'email': auth0user.extra_data['email'],
    }

    return render(request, 'perfil.html', {
        'auth0User': auth0user,
        'userdata': userdata,
        'nombre': user,
    })


def logout(request):
    django_logout(request)
    domain = 'dev-bmi8oyu1.auth0.com'
    client_id = 'YgcE1EravfahIBTJFWC0QOW8vPEugXYs'
    return_to = 'http://localhost:8000'
    return HttpResponseRedirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')

def getUsers(request):
    #usuarios=User.Objects.getall()
    users = User.objects.all()
    return render(request,'perfil_usuarios.html',{'usuarios':users})

def crearFase(request):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    Método para crear fases de un proyecto dado
    """
    if request.method == 'POST': #preguntamos primero si la petición Http es POST
        fase_form = FaseForm(request.POST)
        if fase_form.is_valid():
            fase_form.save()
            return redirect('index')
    else:
        fase_form = FaseForm() #sin parametros ya que se van a cargar los valores en el formulario
    return render(request, 'crear_fase.html', {'fase_form': fase_form})

