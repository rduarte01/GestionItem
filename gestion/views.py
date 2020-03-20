from django.shortcuts import render
# ... other import statements ...
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from post import POST

from .models import Proyecto

from .forms import FormProyecto #, FormUsuario



"""
def agregarUsuarios(request):
    ##MENU PRINCIPAL AL INICIAR SESION
    ####################### USUARIO
    formUsuario = FormUsuario(request.POST or None)   ######## forms con proyecto
    if formUsuario.is_valid():
        instanceUsuario = formUsuario.save(commit=False)########## impide que se guarde a la BD
        if not instanceUsuario.nombre:
            ###### retornar error
            return HttpResponseRedirect("falta completar campos")

        instanceUsuario.save()######## guarda a la BD, en medio se puede manipular el texto
        print(instanceUsuario)
        print(instanceUsuario.timestamp)

    context ={
        "formUsuario": formUsuario,
    }
    return render(request,'agregarUsuarios.html', context)

"""

###### FALTA ENLAZAR Y AGREGAR URL EN LA PLANTILLA PARA LA REDIRECCION
def menu(request):
    """MENU PRINCIPAL AL INICIAR SESION GERENTE"""
    return render(request,'Menu.html')
    """MENU PRINCIPAL AL INICIAR SESION ADMINISTRADOR SISTEMA"""
    #return render(request,'MenuAdminSistema.html')
    """MENU PRINCIPAL EN ESPERA DE ACEPTACION"""
    #return render(request,'MenuEnEspera.html')



"""
obtener datos de la plantilla, cuando se utiliza form
if form.is_valid()
email=form.cleaned_data.get("email")
"""


############ FALTA MEJORAR, ES EL COMIENZO #################
def creacionProyecto(request):
    """PLANTILLA DE FORMULARIO PARA LA CREACION DE UN PROYECTO"""


    ####################### PROYECTO
    formProyecto = FormProyecto(request.POST or None)   ######## forms con proyecto
    if formProyecto.is_valid():
        instanceProyecto = formProyecto.save(commit=False)########## impide que se guarde a la BD
        #agregarUsuarios(request)
       # if not instanceProyecto.nombre:
            ###### retornar error
       #     return HttpResponseRedirect("falta completar campos")

      #  instanceProyecto.save()######## guarda a la BD, en medio se puede manipular el texto
        #print(instanceProyecto)
        #print(instanceProyecto.timestamp)

        instanceProyecto.save()######## guarda a la BD, en medio se puede manipular el texto
    context ={
        "formProyecto": formProyecto,
    }
    return render(request,'creacionProyecto2.html', context)


def index(request):
    """INICIO DE APLICACION, SOLICITUD DE INICIAR SESION"""
    user = request.user
   # return render(request, 'index.html')
    if user.is_authenticated:
        return redirect(menu)
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
    domain = 'ruben-dev.auth0.com'
    client_id = 'q8WImi9pV1hGFO62esYPTyhtoBey1Tlk'
    return_to = 'http://localhost:8000'
    return HttpResponseRedirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')

def getUsers(request):
    """"TRAE INFORMACION DE USUARIO"""
    #usuarios=User.Objects.getall()
    users = User.objects.all()
    return render(request,'perfil_usuarios.html',{'usuarios':users})

