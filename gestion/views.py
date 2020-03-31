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
from .forms import FaseForm, FormUserAgg
from django.db.models import Count
from django.contrib.auth.decorators import permission_required
#### GLOBALES
PROYECTOS_USUARIO=[]
CANTIDAD=1
DELETE=0
from .models import Proyecto,TipoItem,Atributo
from .forms import FormProyecto,TipoItemForm,AtributeForm,SettingsUserForm,RolForm#, FormUsuario
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory
from guardian.shortcuts import assign_perm
from guardian.decorators import permission_required_or_403


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


def menu(request):
    user = request.user
    #return render(request, 'MenuAdminSistema.html')
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


class VerSolicitudesEspera(ListView):
    model = User
    template_name = "ListaUser.html"
    queryset = User.objects.filter(esta_aprobado = False)


#jesus
def ver_usuarios_aprobados(request):
    '''Lista todos los usarios aprobados en el sistema '''
    users=User.objects.filter(esta_aprobado=True).exclude(id=request.user.id)
    context={'users':users}
    return render(request,'usuariosAprobados.html',context)


def get_user(request,pk):
    ''' Sirve para poder asignar o sacar los permisos es_gerente , es_administrador
        y cambiar el estado de un usario en especifico
    '''
    user_active=False
    if( request.method == 'POST' ):
        form=SettingsUserFormJesus(request.POST)
        print(request.POST)
        if(form.is_valid()):
            user = User.objects.get(id=pk)
            is_admin,is_gerente,estado = recoger_datos_usuario_settings(form)
            ban = True
            if estado == 'False': #si el estado es falso
                print('estado Falso')
                if User_Proyecto.objects.filter(user_id=user.id).exists() :  #si el usuario no esta asociado a ningun proyecto
                    proyectos_user= User_Proyecto.objects.filter(user_id=request.user.id)
                    print('si esta asociada a un proyecto')
                    for pu in proyectos_user:
                        if pu.activo:
                            print(pu.proyecto_id)
                            ban=False
                            break
            if ban:
                print ('ban es true')
                add_permission_admin(user, is_admin)
                add_permission_gerente(user, is_gerente)
                user.esta_aprobado = estado
                user.save()
            else:
                contexto={
                    'mesanje_error':'El usuario esta activo en un proyecto por lo tanto no puedes desactivarlo, para hacerlo deben de darle de baja en el proyecto que en donde esta asociado   '

                }
                return render(request,'error.html',contexto)
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
            'form':form,
            'banManager':banManager,
            'banGerente':banGerente
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


def tipo_item_views_create(request,id_fase):
    '''Sirve para crear un tipo de item,en una fase en especifica'''
    if request.method == "POST":
        my_form=TipoItemForm(request.POST)
        if(my_form.is_valid()):
           nombre_ti,cantidad_atributos_ti=recoger_datos_tipo_item(my_form)
           return redirect('gestion:add_atribute',nombre_ti=nombre_ti,cantidad_atributos=cantidad_atributos_ti,fase_id=id_fase)
    else:
        my_form= TipoItemForm()
        fase=Fase.objects.get(id_Fase=id_fase)
        proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto_id)
        context={
            'tipo_item_form': my_form,
            'proyecto':proyecto
           }
        return render(request, 'crear_tipo_item.html', context)
#Vistas agregadas por jesus



def add_atribute(request,nombre_ti,cantidad_atributos,fase_id):
    ''' Sirve para poder crear un nuevo atributo, asociando ese atributo a un tipo de item'''

    my_form = formset_factory(AtributeForm, extra=cantidad_atributos)
    if request.method == 'POST':
        my_form_set=my_form(request.POST)
        if(my_form_set.is_valid()):
            tipo_item=TipoItem(nombre=nombre_ti,fase_id=fase_id)
            tipo_item.save()
            for form in my_form_set:
                n,o,t=recoge_datos_atributo(form)
                atributo1=Atributo.objects.create(nombre=n,es_obligatorio=o,tipo_dato=t,ti_id=tipo_item.id_ti)
            return redirect('gestion:get_fase_proyecto', id_fase=fase_id)
    else:
        contexto={'formset':my_form,
                 'cant_atributos': list(range(1,cantidad_atributos+1))
                }
        return render(request,'crear_atributo.html',contexto)


#jesus
def recoger_datos_tipo_item(my_form):
    '''Sirve para recoger los datos despues de un POST en un formulario de tipo de item, retorna el
        valor del nombre del tipo de item y la cantidad de atributos del tipo de item
    '''
    nombre = my_form.cleaned_data['nombre']
    valor = my_form.cleaned_data['cantidad']
    return nombre,valor

#jesus
def recoge_datos_atributo(form):
    '''Sirve para recoger los datos despues de un POST en un formulario de atributo, retorna el
            valor del nombre del atributo, si es obligatorio, y el tipo de dato
    '''
    nombre_atributo = form.cleaned_data.get('nombre')
    obligatoriedad = form.cleaned_data.get('es_obligatorio')
    tipo_dato_atibuto = form.cleaned_data.get('tipo_dato')
    return nombre_atributo,obligatoriedad,tipo_dato_atibuto

#jesus
def recoger_datos_usuario_settings(form):
    '''Sirve para recoger los datos despues de un POST en un formulario de UsuarioSetting, retorna tres valores
        dos booleanos para determinar si es gerente y administrador y el estado del usuario
    '''
    is_admin = form.cleaned_data['is_admin']
    is_gerente = form.cleaned_data['is_manager']
    estado = form.cleaned_data['estado']
    return is_admin,is_gerente,estado


def add_permission_admin(user,is_admin):
    '''Funcion que permite agregar o sacar el permiso es_administrador a un usario, no retorna nada'''
    content_type = ContentType.objects.get_for_model(User)
    if (is_admin):  # se agrega el es_administrador
        permission = Permission.objects.get(content_type=content_type, codename='es_administrador')
        user.user_permissions.add(permission)
    else:  # se elimina el permiso es_administrador
        name_permission = 'es_administrador'
        permission = Permission.objects.get(content_type=content_type, codename=name_permission)
        user.user_permissions.remove(permission)


def add_permission_gerente(user,is_gerente):
    '''Funcion que permite agregar o sacar el permiso is_gerente a un usario, no retorna nada'''
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
            assign_perm('is_gerente', request.user, x)
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
    print(PROYECTOS_USUARIO)
    print(proyectos)
    cant = len(PROYECTOS_USUARIO)

    context={
        'proyectos':proyectos,###### TODOS LOS PROYECTOS
        'list': PROYECTOS_USUARIO,##PROYECTOS DEL USUARIO LOS CUAL SE DEBE MOSTRAR, SOLO ID
        'cant': cant####CANTIDAD DE PROYECTOS QUE POSEE
    }
    return render(request, 'verProyectos.html', context)


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

def ver_proyecto(request,pk):
    proyecto=Proyecto.objects.get(id_proyecto=pk)
    fases = Fase.objects.filter(id_Proyecto_id=pk)
    contexto={
        'proyecto':proyecto,
        'fases':fases
    }
    return render(request,'opcionesProyecto.html',contexto)

def get_fase_proyecto(request,id_fase):
    fase=Fase.objects.get(id_Fase=id_fase)
    proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto_id)
    contexto={
        'fase':fase,
        'proyecto':proyecto
    }
    return render(request,'opcionesFase.html',contexto)

def importar_tipo_item(request,id_fase):
    '''esta funcion permite importar tipos de item en un proyecto , filtrando aquellos tipo
        items de los proyectos de los que esta asociado el usuario y que aun no se tenga en  las
        fases dell proyecto.
    '''

    if(request.method=='POST'):
        print('es post')
        some_var = request.POST.getlist('checkbox')
        for id in some_var:
            print (id_fase)
            ti=TipoItem.objects.get(id_ti=id)#capturamos el tipo de item
            atributos=Atributo.objects.filter(ti_id=id) #optenemos todos los atributos de ese tipo de item
            ti.id_ti=None #clonamos el tipo de item
            ti.fase_id=id_fase
            ti.save() #guardamos
            for atributo in atributos: #iteramos cada atributo clonarlos y relacionar con el tipo de item nuevo
                    atributo.id_atributo=None
                    atributo.ti_id=ti.id_ti
                    atributo.save()
        return redirect('gestion:get_fase_proyecto',id_fase=id_fase)
    else:
        print('es get')
        user=request.user #se optiene el usuario
        list_tipo_item_a_importar=[]
        list_tipo_item=[]
        list_tipo_item_proyecto_actual=get_all_tipo_item(Fase.objects.get(id_Fase=id_fase).id_Proyecto_id)
        proyectos=User_Proyecto.objects.exclude(proyecto_id=Fase.objects.get(id_Fase=id_fase).id_Proyecto_id)#obtengo el proyectos que el usuario tiene acceso
        print('aca')
        print(list_tipo_item_proyecto_actual)
        for proyecto in proyectos:
            fases=Fase.objects.filter(id_Proyecto_id=proyecto.proyecto_id) #obtengo toda las fases del proyecto
            list_tipo_item=[]
            for fase in fases :
                list_tipo_item+=TipoItem.objects.filter(fase_id=fase.id_Fase)
            for ti in list_tipo_item :
                if not ti.nombre in list_tipo_item_proyecto_actual:
                    list_tipo_item_a_importar += [ti]

        print(list_tipo_item_a_importar)
        fase=Fase.objects.get(id_Fase=id_fase)
        proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto_id)
        contexto={
            'tipoItems':list_tipo_item_a_importar,
            'proyecto':proyecto
        }
        return render(request,'listaTipoItem.html',contexto)

def get_all_tipo_item(id_proyecto):
    '''Esta funcion permite obtener todos los tipos de item de un proyecto especifico'''

    fases=Fase.objects.filter(id_Proyecto_id=id_proyecto)
    list_tipo_item=[]
    list_tipo_item_name=[]
    for fase in fases:
        list_tipo_item += TipoItem.objects.filter(fase_id=fase.id_Fase)    #optenemos todos los objetos del tipo de item

    for ti in list_tipo_item:
        list_tipo_item_name+=[ti.nombre] # de todos los objetos obtenemos el nombr

    print("esto imprimo aca")
    print(list_tipo_item_name)
    return  list_tipo_item_name