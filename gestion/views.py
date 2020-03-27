from django.core.mail import EmailMessage
from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission,Group
#from post import POST
from .models import Proyecto,TipoItem,Atributo
from .forms import FormProyecto,TipoItemForm,AtributeForm,SettingsUserForm#, FormUsuario
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory


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
    user = request.user

    if(user.esta_aprobado):
        if user.has_perm('auth.es_administrador'):
             return render(request,'MenuAdminSistema.html')
        else:
            return render(request, 'Menu.html')
    else:
        return render(request, 'MenuEnEspera.html')

       #     CorreoMail()
            #correo = str(User) + '@gmail.com'
            #mensaje='favor verificar si el usuario cumple los requisitos para ser aceptado'#+ str(User)
            #CorreoMail('Usuario en Espera',mensaje,'rduarte0997@qgmail.com')
        """
        obtener datos de la plantilla, cuando se utiliza form
        if form.is_valid()
        email=form.cleaned_data.get("email")
        """

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
        'estado': user.esta_aprobado,
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



def ver_usuarios_aprobados(request):
    users=User.objects.filter(esta_aprobado=True)
    context={'users':users}
    return render(request,'usuariosAprobados.html',context)


def get_user(request,pk):
    if( request.method == 'POST' ):
        form=SettingsUserForm(request.POST)
        print(request.POST)
        if(form.is_valid()):
            user = User.objects.get(id=pk)
            is_admin,is_gerente,estado = recoger_datos_usuario_settings(form)
            add_permission_admin(user,is_admin)
            add_permission_gerente(user,is_gerente)
            user.esta_aprobado=estado
            user.save()
        else:
            print("no es valido")

        return redirect('ver_usuarios_aprobados')
    else:
        usuario=User.objects.get(id=pk)
        banManager=request.user.has_perm('proyecto.is_gerente')
        banGerente=request.user.has_perm('auth.is_administrador')
        print(banGerente,banManager)
        form=SettingsUserForm()
        context = {
            'user': usuario,
            'form':form
        }
        return render(request,"perfilUsuario.html",context)

#Vistas agregadas por jesus
def tipo_item_views_create(request):
    global CANTIDAD_ATRIBUTOS_TI,NOMBRE_TI
    if request.method == "POST":
        my_form=TipoItemForm(request.POST)
        if(my_form.is_valid()):
           nombre_ti,cantidad_atributos_ti=recoger_datos_tipo_item(my_form)
           return redirect('add_atribute',nombre_ti=nombre_ti,cantidad_atributos=cantidad_atributos_ti)
    else:
        my_form= TipoItemForm()
        context={
            'tipo_item_form': my_form
           }
        return render(request, 'crear_tipo_item.html', context)



def add_atribute(request,nombre_ti,cantidad_atributos):
    my_form = formset_factory(AtributeForm, extra=cantidad_atributos)
    if request.method == 'POST':
        my_form_set=my_form(request.POST)
        if(my_form_set.is_valid()):
            tipo_item=TipoItem(nombre=nombre_ti)
            tipo_item.save()
            for form in my_form_set:
                n,o,t=recoge_datos_atributo(form)
                atributo1=Atributo.objects.create(nombre=n,es_obligatorio=o,tipo_dato=t,ti_id=tipo_item.id_ti)
            return redirect('menu')
    else:
        contexto={'formset':my_form,
                 'cant_atributos': list(range(1,cantidad_atributos+1))
                }
        return render(request,'crear_atributo.html',contexto)

def recoger_datos_tipo_item(my_form):
    nombre = my_form.cleaned_data['nombre']
    valor = my_form.cleaned_data['cantidad']
    return nombre,valor


def recoge_datos_atributo(form):
    nombre_atributo = form.cleaned_data.get('nombre')
    obligatoriedad = form.cleaned_data.get('es_obligatorio')
    tipo_dato_atibuto = form.cleaned_data.get('tipo_dato')
    return nombre_atributo,obligatoriedad,tipo_dato_atibuto


def recoger_datos_usuario_settings(form):
    is_admin = form.cleaned_data['is_admin']
    is_gerente = form.cleaned_data['is_manager']
    estado = form.cleaned_data['estado']
    return is_admin,is_gerente,estado


def add_permission_admin(user,is_admin):
    content_type = ContentType.objects.get_for_model(User)
    if (is_admin):  # se agrega el es_administrador
        permission = Permission.objects.get(content_type=content_type, codename='es_administrador')
        user.user_permissions.add(permission)
    else:  # se elimina el permiso es_administrador
        name_permission = 'es_administrador'
        permission = Permission.objects.get(content_type=content_type, codename=name_permission)
        user.user_permissions.remove(permission)


def add_permission_gerente(user,is_gerente):
    content_type = ContentType.objects.get_for_model(Proyecto)
    if (is_gerente):  # se agrega el es_administrador
        permission = Permission.objects.get(content_type=content_type, codename='is_gerente')
        user.user_permissions.add(permission)
    else:  # se elimina el permiso es_administrador
        name_permission = 'is_gerente'
        permission = Permission.objects.get(content_type=content_type, codename=name_permission)
        user.user_permissions.remove(permission)
