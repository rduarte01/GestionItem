from django.shortcuts import render
# ... other import statements ...
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User

###### FALTA ENLAZAR Y AGREGAR URL EN LA PLANTILLA PARA LA REDIRECCION
def menu(request):
    """MENU PRINCIPAL AL INICIAR SESION"""
    return render(request,'menu.html')


def index(request):
    """INICIO DE APLICACION, SOLICITUD DE INICIAR SESION"""
    user = request.user
    return render(request, 'index.html')
    if user.is_authenticated:
        return redirect(perfil)
    else:
        return render(request, 'index.html')


# ... index, profile ...


@login_required
def perfil(request):
    """SOLICITUD DE AUTENTICACION PARA MOSTRAR EL PERFIL DEL USUARIO"""
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
        'userdata': json.dumps(userdata, indent=4)
    })


def logout(request):
    """PARA DESLOGUEARSE"""
    django_logout(request)
    domain = 'dev-bmi8oyu1.auth0.com'
    client_id = 'YgcE1EravfahIBTJFWC0QOW8vPEugXYs'
    return_to = 'http://djangoproyect.herokuapp.com'
    return HttpResponseRedirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')

def getUsers(request):
    """"TRAE INFORMACION DE USUARIO"""
    #usuarios=User.Objects.getall()
    users = User.objects.all()
    return render(request,'perfil_usuarios.html',{'usuarios':users})

