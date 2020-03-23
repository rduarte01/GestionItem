from django.core.mail import EmailMessage
from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission,Group
#from post import POST


from .models import Proyecto,TipoItem,Atributo
from .forms import FormProyecto,TipoItemForm,AtributeForm, estadoUsuario#, FormUsuario

CANTIDAD_ATRIBUTOS_TI=1
NOMBRE_TI="hola"
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
    return render(request,'MenuAdminSistema.html')
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




@login_required
@permission_required('auth.es_admin', raise_exception=True)
def verSolicitudesenEspera(request):
    """Si el usuario que solicita la pagina es staff(ADMINISTRADOR)
    entonce carga los usuarios que esperan ser aprobados y lo manda a
    a la pagina ListaUser que muestra la lista. Caso contrario muestra
    una pagina de que no es administrador"""
    print("Si sos Admin")

    users = User.objects.filter(esta_aprobado=False)

    return render(request,'ListaUser.html',{
    'usuarios': users,
    })



#Vistas agregadas por jesus
def tipo_item_views_create(request):
    global CANTIDAD_ATRIBUTOS_TI,NOMBRE_TI
    if request.method == "POST":
        my_form=TipoItemForm(request.POST)
        if(my_form.is_valid()):
           NOMBRE_TI,CANTIDAD_ATRIBUTOS_TI=recoger_datos_tipo_item(my_form)
        return redirect('add_atribute')
    else:
        my_form= TipoItemForm()
        context={
            'tipo_item_form': my_form
           }
        return render(request, 'crear_tipo_item.html', context)


from django.forms import formset_factory

def add_atribute(request):
    my_form = formset_factory(AtributeForm, extra=CANTIDAD_ATRIBUTOS_TI)
    if request.method == 'POST':
        my_form_set=my_form(request.POST)
        if(my_form_set.is_valid()):
            #tipo_item=TipoItem(nombre=NOMBRE_TI)
            #tipo_item.save()
            #print(tipo_item.id_ti)
            for form in my_form_set:
               # nombre_atributo,es_obligatorio,tipo_dato=recoge_datos_atributo(form)
                #atributo=Atributo(nombre=nombre_atributo,es_obligatorio=obligatoriedad,
                 #                 tipo_dato=tipo_dato_atibuto,
                  #                ti=tipo_item.id_ti
                  #                )
                #atributo.save()
                pass
        return redirect('menu')
    else:
        contexto={'formset':my_form,
                 'cant_atributos': list(range(1,CANTIDAD_ATRIBUTOS_TI+1))
                }
        return render(request,'crear_atributo.html',contexto)



def recoger_datos_tipo_item(my_form):
    nombre = my_form.cleaned_data['nombre']
    valor = my_form.cleaned_data['cantidad']
    return nombre,valor


def recoge_datos_atributo(my_form):
    nombre_atributo = form.cleaned_data.get('nombre')
    obligatoriedad = form.cleaned_data.get('es_obligatorio')
    tipo_dato_atibuto = form.cleaned_data.get('tipo_dato')
    return nombre_atributo,obligatoriedad,tipo_dato_atibuto