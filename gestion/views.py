from django.core.mail import EmailMessage
from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission,Group
from django.views.generic import TemplateView,ListView,UpdateView, CreateView
from django.urls import reverse_lazy
from .models import Proyecto, Auditoria, User_Proyecto,Fase
from .forms import FormProyecto,FormAyuda,SettingsUserFormJesus
from time import gmtime, strftime
from .forms import FaseForm, FormUserAgg,FormProyectoEstados
from django.db.models import Count
from django.contrib.auth.decorators import permission_required
from .models import Proyecto,TipoItem,Atributo
from .forms import FormProyecto,TipoItemForm,AtributeForm,SettingsUserForm,RolForm#, FormUsuario
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory

#### GLOBALES
PROYECTOS_USUARIO=[]
CANTIDAD=1
DELETE=0

def estadoProyecto(request,pk):
    """ RECIBE EL ID DEL PROYECTO A CAMBIAR SU ESTADO Y EL ESTADO NUEVO MEDIANTE EL POST"""
    form=FormProyectoEstados(request.POST)
    p = Proyecto.objects.get(id_proyecto=pk)  ##### BUSCA EL PROYECTO CON ID

    if form.is_valid():
        x=form.cleaned_data
        z=x.get("estado")#### ESTADO SELECCIONADO
        #print(z)
        #print(pk)

        if(z=="FINALIZADO"):
            return redirect('gestion:listar_proyectos')### VUELVE A LISTAR LOS PROYECTOS DEL USUARIO
        elif(z=="INICIADO"):
            p.estado=z####### SE ASIGNA ESTADO
            p.save()##### SE GUARDA
            return redirect('gestion:listar_proyectos')### VUELVE A LISTAR LOS PROYECTOS DEL USUARIO
        elif(z=="CANCELADO"):
            p.estado=z####### SE ASIGNA ESTADO
            p.save()##### SE GUARDA
            return redirect('gestion:listar_proyectos')### VUELVE A LISTAR LOS PROYECTOS DEL USUARIO

    context={
        "form":form,
        "estado": p.estado,
    }
    return render(request, 'estadoProyecto.html',context)


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
    """DESPLIEGA UN APARTADO EN DONDE EL USUARIO INGRESA SU DUDA O INCONVENIENTE Y SE ENVIA A LOS DESARROLLADORES
    DEL SISTEMA DE MODO A ACLARAR O SOLUCIONAR INQUIETUDES
    """
    form = FormAyuda(request.POST)
    if form.is_valid():
        user=request.user
        mensajeOBJ = form.cleaned_data
        mensaje = mensajeOBJ.get("Consulta")
        asunto= "Inconveniente o consulta de: "+ str(user)
        guardarAuditoria = "El usuario envio la siguiente consulta o inquietud: "+ mensaje
        registrarAuditoria(request.user, guardarAuditoria)

        CorreoMail(asunto,mensaje,"waltergautofcb@gmail.com")
        return redirect('gestion:menu')

    context={
        "form":form,
    }
    registrarAuditoria(request.user,'Ingreso en el apartado contactos')
    return render(request,'Contactos.html', context)



def CantProyectos(request):
    """ RETORNA LA LISTA DE ID DE LOS PROYECTOS ASOCIADOS AL USUARIO ACTUAL """
    user = request.user#### SE UTILIZA PARA QUITAR EL ID DEL USUARIO ACTUAL
    NroProyectos = User_Proyecto.objects.all()### QUERY DE TODOS LOS PROYECTOS
    GuardaProyectos=[]### GUARDA LOS PROYECTOS EN LOS QUE SE ENCUENTRA ASOCIADO EL USUARIO

    for i in range(NroProyectos.count()):###### RECORRE TODOS LOS PROYECTOS
        if (NroProyectos[i].user_id==user.id):#### CONSULTA SI EL PROYECCTO PERTENECE AL USUARIO
            GuardaProyectos.append(NroProyectos[i].proyecto_id)###### GUARDA EL ID PROYECTO DEL USUARIO
            #print(NroProyectos[i])
    return GuardaProyectos

@login_required
def menu(request):
    user = request.user

    if( user.esta_aprobado):
        if user.has_perm('auth.es_administrador'):
             return render(request,'MenuAdminSistema.html')
        else:
            return render(request, 'Menu.html')
    else:
        registrarAuditoria(request.user ,'Inicio Menu en espera de aprobacion')
        #si no tiene rol le tira el menu de espera
        #envia correo al admin para que acepte
        correo='rduarte0997@gmail.com'
        #correo de administrador del sistema
        asunto='Solicitud de ingreso al sistema'
        mensaje='favor verificar si el usuario cumple los requisitos para ser aceptado'+ str(User)
        CorreoMail(asunto,mensaje,correo)
        #si no tiene rol le tira el menu de espera
        user=request.user
        #envia correo a usuario en espera para que espere
        asunto='Se encuentra en verificacion favor aguarde'
        correo = user.email   #correo de administrador del sistema
        mensaje='Gracias por registrarte en nuestro sistema, favor aguardar a ser aceptado por el administrador del sistema usuario: '+ str(User)
       # CorreoMail(asunto,mensaje,correo)
        return render(request, 'MenuEnEspera.html')
 
def creacionProyecto(request):
    """PLANTILLA DE FORMULARIO PARA LA CREACION DE UN PROYECTO"""

    registrarAuditoria(request.user,'Selecciono creacion de proyecto')

    formProyecto = FormProyecto(request.POST or None)   ######## forms con proyecto

    if formProyecto.is_valid():
        instanceProyecto = formProyecto.save(commit=False)########## impide que se guarde a la BD

        ### NADA QUE TOCAR

        instanceProyecto.save()######## guarda a la BD, en medio se puede manipular el texto

        global CANTIDAD

        cantidad = formProyecto.cleaned_data

        cantidad_fases=cantidad.get("fase")##### PARA WALTER

        CANTIDAD=cantidad_fases-1

        q = cantidad.get("users")
        z= Proyecto.objects.last()
        id_proyecto = z.id_proyecto ## ID DEL PROYECTO CREADO
        x=q.count()##### CANTIDAD DE PROYECTOS
        registrarAuditoria(request.user,'Creo el proyecto: '+str(cantidad.get("nombre")))

        for i in range(x):###### SE GUARDAN EN USER_PROYECTOS LAS RELACIONES
            registrarAuditoria(request.user, 'En el proyecto: ' + str(cantidad.get("nombre")+' añadio al usuario: '+str(q[i])+' en el proyecto'))
            id_user =q[i].id
            p = User_Proyecto(user_id= id_user ,proyecto_id= id_proyecto,activo= True)
            p.save()

        return redirect('gestion:crearFase')


    context ={
        "formProyecto": formProyecto,
    }

    return render(request,'creacionProyecto2.html', context)


def index(request):
    """INICIO DE APLICACION, SOLICITUD DE INICIAR SESION DEL SISTEMA, SOLO SE MUESTRA SI NO SE ESTA REGISTRADO EN EL SSO"""
    user = request.user
    if user.is_authenticated:
        return redirect('gestion:menu')
    else:
        return redirect('gestion:menu')


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
        'estado': user.esta_aprobado,
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



class VerSolicitudesEspera(ListView):
    model = User
    template_name = "ListaUser.html"
    queryset = User.objects.filter(esta_aprobado = False)
def ver_usuarios_aprobados(request):
    users=User.objects.filter(esta_aprobado=True)
    context={'users':users}
    return render(request,'usuariosAprobados.html',context)


def get_user(request,pk):
    if( request.method == 'POST' ):
        form=SettingsUserFormJesus(request.POST)
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

        return redirect('gestion:ver_usuarios_aprobados')
    else:
        usuario=User.objects.get(id=pk)
        banManager=request.user.has_perm('proyecto.is_gerente')
        banGerente=request.user.has_perm('auth.is_administrador')
        print(banGerente,banManager)
        form=SettingsUserFormJesus()
        context = {
            'user': usuario,
            'form':form
        }
        return render(request,"perfilUsuario.html",context)


class ActualizarUser(UpdateView):
    model = User
    form_class = SettingsUserForm
    template_name = 'perfilUsuario.html'
    success_url = reverse_lazy('gestion:listaDeEspera')

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        request.POST['username']  += 'GER'
        return super(ActualizarUser,self).post(request,**kwargs)

class CrearRol(CreateView):
    model = Group
    form_class = RolForm
    template_name = "CrearRol.html"
    success_url = reverse_lazy("gestion:menu")



def tipo_item_views_create(request):
    global CANTIDAD_ATRIBUTOS_TI,NOMBRE_TI
    if request.method == "POST":
        my_form=TipoItemForm(request.POST)
        if(my_form.is_valid()):
           nombre_ti,cantidad_atributos_ti=recoger_datos_tipo_item(my_form)
           return redirect('gestion:add_atribute',nombre_ti=nombre_ti,cantidad_atributos=cantidad_atributos_ti)
    else:
        my_form= TipoItemForm()
        context={
            'tipo_item_form': my_form
           }
        return render(request, 'crear_tipo_item.html', context)
#Vistas agregadas por jesus



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
            return redirect('gestion:menu')
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



"""
SE PASA LA CANTIDAD DE FASES
"""
def crearFase(request):

    fase = FaseForm(request.POST)
    global CANTIDAD
    cantidad = CANTIDAD
    if fase.is_valid():
        x = Proyecto.objects.last()
        nombreFase = fase.cleaned_data.get("nombre")
        descFase = fase.cleaned_data.get("descripcion")
        z = Fase(nombre=nombreFase,descripcion=descFase,id_Proyecto=x)
        z.save()

        if cantidad != 0:
            cantidad = cantidad - 1
            CANTIDAD = cantidad
            return redirect('gestion:crearFase')
        else:
            return redirect('gestion:menu')

    context = {
    'form': fase
    }
    return render(request, 'crear_fase.html', context)


def listar_auditoria(request):
    """ LISTA LOS REGISTROS DE LA TABLA AUDITORIA """
    registrarAuditoria(request.user, 'Ingreso al apartado Auditoria')
    auditoria = Auditoria.objects.all()
    context={
        'auditoria':auditoria
    }
    return render(request, 'Auditoria.html', context)


### SE PUEDE USAR DESPUES
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


def listar_proyectos(request):
    """ LISTA LOS PROYECTOS DEL USUARIO"""
    registrarAuditoria(request.user, 'Lista sus proyectos existentes')
    proyectos = Proyecto.objects.all()

    ### PROYECTOS_USUARIO
    PROYECTOS_USUARIO= CantProyectos(request)
    #print(PROYECTOS_USUARIO)
    #print(proyectos)
    cant = len(PROYECTOS_USUARIO)

    context={
        'proyectos':proyectos,###### TODOS LOS PROYECTOS
        'list': PROYECTOS_USUARIO,##PROYECTOS DEL USUARIO LOS CUAL SE DEBE MOSTRAR, SOLO ID
        'cant': cant####CANTIDAD DE PROYECTOS QUE POSEE
    }
    return render(request, 'verProyectos.html', context)


def detallesProyecto(request,pk):
    proyectos = Proyecto.objects.get(id_proyecto=pk)
    #print(proyectos)
    #fases = Fase.objects.get(id_Proyecto=proyectos)
    fases= Fase.objects.all()
    #print(fases[0].id_Proyecto)
    context={
        "proyectos":proyectos,
        "fases":fases,
    }
    return render(request, 'detallesProyecto.html', context)

def proyectoCancelado(request):
    x = Proyecto.objects.last()
    instanceFase = Fase.objects.filter(id_Proyecto = x.id_proyecto)
    for i in instanceFase:
        i.delete()

    instanceUser = User_Proyecto.objects.filter(proyecto_id = x.id_proyecto)
    for i in instanceUser:
        i.delete()


    instanceProyecto = Proyecto.objects.filter(id_proyecto=x.id_proyecto)
    for i in instanceProyecto:
        i.delete()

    return  redirect("gestion:menu")




