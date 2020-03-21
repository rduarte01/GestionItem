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
from .forms import FormProyecto,TipoItemForm#, FormUsuario


def CorreoMail():
    #correo='waltergautofcb@gmail.com'
    #correo='gerardocabrer@gmail.com'
    correo='jesusromanm99@gmail.com'

    mail=EmailMessage('Un Usuario en espera','Verifica al usuario ta..',to={correo})
    mail.send()



def Contactos(request):
    return render(request,'Contactos.html')

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
    CorreoMail()
    #correo = str(User) + '@gmail.com'
    #mensaje='favor verificar si el usuario cumple los requisitos para ser aceptado'#+ str(User)
    #CorreoMail('Usuario en Espera',mensaje,'rduarte0997@qgmail.com')
    return render(request,'MenuEnEspera.html')



"""
obtener datos de la plantilla, cuando se utiliza form
if form.is_valid()
email=form.cleaned_data.get("email")
"""



def creacionProyecto(request):
    """PLANTILLA DE FORMULARIO PARA LA CREACION DE UN PROYECTO"""

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
    """PARA DESLOGUEARSE"""
    django_logout(request)
    #modificar para mi app
    domain = 'ruben-dev.auth0.com'
    client_id = 'q8WImi9pV1hGFO62esYPTyhtoBey1Tlk'
    return_to = 'http://localhost:8000'
    return HttpResponseRedirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')

def getUsers(request):
    """"TRAE INFORMACION DE USUARIO"""
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



#Vistas agregadas por jesus
def tipo_item_views_create(request):
    if request.method == "POST":
        tipo_item_form=TipoItemForm(request.POST)
        if(tipo_item_form.is_valid()):
            print(tipo_item_form)

    print("es un metodo get")
    tipo_item_form= TipoItemForm()
    context={
            'tipo_item_form': tipo_item_form
        }
    return render(request, 'crear_tipo_item.html', context)