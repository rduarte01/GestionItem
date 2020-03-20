from django.shortcuts import render
# ... other import statements ...
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User


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
    """"Realiza consultas de los datos del usuario que esta realizando la
    solicitud, y lo envia al html, para asi mostrarselo sus datos de ese usuario"""
    user = request.user
    auth0user = user.social_auth.filter(provider='auth0')[0]

    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'estado': user.is_approbated,
        'picture': auth0user.extra_data['picture'],
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

@login_required
def verSolicitudesenEspera(request):
    """Si el usuario que solicita la pagina es staff(ADMINISTRADOR)
    entonce carga los usuarios que esperan ser aprobados y lo manda a
    a la pagina ListaUser que muestra la lista. Caso contrario muestra
    una pagina de que no es administrador"""
    user = request.user
    if user.is_staff is True:
        print("Si sos Admin")
        users = User.objects.filter(is_approbated=False)
        return render(request,'ListaUser.html',{
        'usuarios': users,
        })
    else:
        print("No sos Admin")
