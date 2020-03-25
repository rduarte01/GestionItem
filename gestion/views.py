from django.core.mail import EmailMessage
from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission,Group
from .models import Proyecto, Auditoria, User_Proyecto
from .forms import FormProyecto
from time import gmtime, strftime
from .forms import FaseForm, FormUserAgg
from django.db.models import Count


def registrarAuditoria(user,accion):
    """FUNCION QUE REGISTRA EN LA  TABLA AUDITORIA LO QUE SE REALIZA EN EL SISTEMA"""
    showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    p = Auditoria(usuario= user,fecha=showtime, accion=accion)###### FALTA ARREGLAR USER
    p.save()


def CorreoMail(asunto,mensaje,correo):
    """ FUNCION QUE RECIBE UN ASUNTO, MENSAJE Y UN CORRREO ELECTRONICO AL CUAL SE LE ENVIA UN CORREO
    ELECTRONICO DE ACUERDO A UNA ACCION"""
    mail=EmailMessage(asunto,mensaje,to={correo})
    mail.send()

def Contactos(request):
    """MUESTRA UN CORREO EN DONDE PUEDE CONTACTAR CON NOSOTROS"""
    registrarAuditoria(request.user ,'Ingreso en el apartado contactos')
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

    return render(request,'MenuAdminSistema.html')

    registrarAuditoria(request.user ,'Inicio Menu del Gerente')

    # falta if de consulta si es gerente
    return render(request,'Menu.html')

    registrarAuditoria(request.user ,'Inicio Menu en espera de aprobacion')

    #si no tiene rol le tira el menu de espera
    #envia correo al admin para que acepte
    correo='rduarte0997@gmail.com'
    #correo de administrador del sistema
    asunto='Solicitud de ingreso al sistema'
    mensaje='favor verificar si el usuario cumple los requisitos para ser aceptado'+ str(User)
    CorreoMail(asunto,mensaje,correo)

    #si no tiene rol le tira el menu de espera
    #envia correo a usuario en espera para que espere
    correo = str(User) + '@gmail.com'   #correo de administrador del sistema
    asunto='Se encuentra en verificacion favor aguarde'
    mensaje='Gracias por registrarte en nuestro sistema, favor aguardar a ser aceptado por el administrador del sistema usuario: '+ str(User)
    CorreoMail(asunto,mensaje,correo)

    return render(request,'MenuEnEspera.html')


def creacionProyecto(request):
    """PLANTILLA DE FORMULARIO PARA LA CREACION DE UN PROYECTO"""

    registrarAuditoria(request.user,'Selecciono creacion de proyecto')

    formProyecto = FormProyecto(request.POST or None)   ######## forms con proyecto
    if formProyecto.is_valid():
        instanceProyecto = formProyecto.save(commit=False)########## impide que se guarde a la BD

        cantidad = formProyecto.cleaned_data
        q = cantidad.get("users")
        q.count()
        id_proyecto = Proyecto.objects.all().count()+1
        x=q.count()
        registrarAuditoria(request.user,'Creo el proyecto: '+str(cantidad.get("nombre")))

        for i in range(x):
            registrarAuditoria(request.user, 'En el proyecto: ' + str(cantidad.get("nombre")+' añadio al usuario: '+str(q[i])+' en el proyecto'))
            id_user =q[i].id
            p = User_Proyecto(user_id= id_user ,proyecto_id= id_proyecto,activo= True)
            p.save()
        instanceProyecto.save()######## guarda a la BD, en medio se puede manipular el texto

        return redirect('crearFase')

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

    registrarAuditoria(request.user, 'Ingreso en el apartado perfil')

    user = request.user
    auth0user = user.social_auth.filter(provider='auth0')[0]
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'estado': user.is_approbated,
        'picture': auth0user.extra_data['picture'],
    }
    registrarAuditoria(request.user ,'Selecciono creacion de proyecto')

    return render(request, 'perfil.html', {
        'auth0User': auth0user,
        'userdata': userdata,
        'nombre': user,
    })


def logout(request):
    """PARA DESLOGUEARSE, CERRAR SESION DEL SSO VUELVE A MOSTRAR INICIO"""

    registrarAuditoria(request.user,'Cerro sesión')

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



"""
SE PASA LA CANTIDAD DE FASES
"""

def crearFase(request):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    Método para crear fases de un proyecto dado
    """
   #if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
    fase_form = FaseForm(request.POST)
    if fase_form.is_valid():
        fase_form.save()
    fase_form = FaseForm() #sin parametros ya que se van a cargar los valores en el formulario
    return render(request, 'crear_fase.html', {'fase_form': fase_form})


def listar_auditoria(request):
    """ LISTA LOS REGISTROS DE LA TABLA AUDITORIA"""

    registrarAuditoria(request.user, 'Ingreso al apartado Auditoria')

    auditoria = Auditoria.objects.all()
    context={
        'auditoria':auditoria
    }
    return render(request, 'Auditoria.html', context)



def listar_usuarios_registrar(request):
    """ LISTA LOS USUARIOS PARA AGREGAR AL PROYECTO"""
    form = User.objects.all()
    if request.method=='POST':
        print('imprimiio:')
        print(request.POST)
  #  form = FormUserAgg(request.POST)
 #   if form.is_valid():
#        form.save()

    context={
        'form':form
    }
    return render(request, 'AggUser.html', context)


########3 se debe usar para añadir usuarios luego a un proyecto
def AggUser(request):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    Método para crear fases de un proyecto dado
    """
    registrarAuditoria(request.user, 'Ingreso al apartado de registro de usuarios a un proyecto')

    #if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
    form = FormUserAgg(request.POST)
    if form.is_valid():
        form.save()
     #sin parametros ya que se van a cargar los valores en el formulario
    return render(request, 'AggUser.html', {'form': form})

