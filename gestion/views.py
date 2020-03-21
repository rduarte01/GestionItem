from django.core.mail import EmailMessage
from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission,Group
#from post import POST
from .models import Proyecto
from .forms import FormProyecto #, FormUsuario


def CorreoMail(asunto,mensaje,correo):
    """ FUNCION QUE RECIBE UN ASUNTO, MENSAJE Y UN CORRREO ELECTRONICO AL CUAL SE LE ENVIA UN CORREO
    ELECTRONICO DE ACUERDO A UNA ACCION"""
    mail=EmailMessage(asunto,mensaje,to={correo})
    mail.send()



def Contactos(request):
    """MUESTRA UN CORREO EN DONDE PUEDE CONTACTAR CON NOSOTROS"""
    return render(request,'Contactos.html')


###### FALTA FILTRAR POR PERMISOS

def menu(request):
    """
    DE ACUERDO AL ROL DEL USUARIO MUESTRA EL MENU CORRESPONDIENTE, SIENDO LOS MENUS:
    MENU PRINCIPAL AL INICIAR SESION GERENTE, MENU PRINCIPAL AL INICIAR SESION ADMINISTRADOR SISTEMA,
    MENU PRINCIPAL EN ESPERA DE ACEPTACION
    AL USUARIO QUE SE REGISTRE POR PRIMERA VEZ SE CREARA UN CORREO Y SE ENVIARA AL ADMINISTRADOR DEL SISTEMA
    SOBRE LA SOLICITUD Y AL USUARIO EN ESPERA PARA QUE AGUARDE A QUE SEA ACEPTADO
    """
    if user.is_staff is True:
        return render(request,'MenuAdminSistema.html')

    # falta if de consulta si es gerente
    return render(request,'Menu.html')

    #si no tiene rol le tira el menu de espera
    #envia correo al admin para que acepte
    correo = 'rduarte0997@gmail.com'   #correo de administrador del sistema
    asunto='Solicitud de ingreso al sistema'
    mensaje='favor verificar si el usuario cumple los requisitos para ser aceptado'+ str(User)
    CorreoMail(asunto,mensaje,correo)

    #si no tiene rol le tira el menu de espera
    #envia correo a usuario en espera para que espere
    correo = str(User) + '@gmail.com'   #correo de administrador del sistema
    asunto='Se encuentra en verificacion favor aguarde'
    mensaje='Favor aguardar a ser aceptado por el administrador del sistema usuario: '+ str(User)
    CorreoMail(asunto,mensaje,correo)

    return render(request,'MenuEnEspera.html')



def creacionProyecto(request):
    """PLANTILLA DE FORMULARIO PARA LA CREACION DE UN PROYECTO"""

    formProyecto = FormProyecto(request.POST or None)   ######## forms con proyecto
    if formProyecto.is_valid():
        instanceProyecto = formProyecto.save(commit=False)########## impide que se guarde a la BD

        ### AGREGAR MODIFICACIONES DE DATOS ANTES DE GUARDAR

        instanceProyecto.save()######## guarda a la BD, en medio se puede manipular el texto
    context ={
        "formProyecto": formProyecto,
    }
    return render(request,'creacionProyecto2.html', context)


def index(request):
    """INICIO DE APLICACION, SOLICITUD DE INICIAR SESION DEL SISTEMA, SOLO SE MUESTRA SI NO SE ESTA REGISTRADO EN EL SSO"""
    user = request.user
    if user.is_authenticated:
        return redirect(menu)
    else:
        return render(request, 'index.html')


@login_required
def perfil(request):
    """SOLICITUD DE AUTENTICACION PARA MOSTRAR EL PERFIL DEL USUARIO||
    Realiza consultas de los datos del usuario que esta realizando la
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
    """PARA DESLOGUEARSE, CERRAR SESION DEL SSO VUELVE A MOSTRAR INICIO"""
    django_logout(request)
    #modificar para mi app
    domain = 'ruben-dev.auth0.com'
    client_id = 'q8WImi9pV1hGFO62esYPTyhtoBey1Tlk'
    return_to = 'http://localhost:8000'
    return HttpResponseRedirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')

def getUsers(request):
    """"TRAE INFORMACION DE USUARIO"""
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
