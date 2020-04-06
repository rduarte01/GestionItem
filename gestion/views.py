from django.core.mail import EmailMessage
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission,Group
from django.views.generic import TemplateView,ListView,UpdateView, CreateView
from django.urls import reverse_lazy
from .models import Proyecto, Auditoria, User_Proyecto,Fase,Permisos,Usuario
from .forms import FormProyecto,FormAyuda,SettingsUserFormJesus,PerfilUserEnEspera,RolForm
from time import gmtime, strftime
from .forms import FaseForm, FormProyectoEstados,FormItem
from django.db.models import Count
from django.utils.decorators import method_decorator
from .models import Proyecto,TipoItem,Atributo,Item,Fase,Atributo_Item,Relacion,Versiones
from .forms import FormProyecto,TipoItemForm,AtributeForm,RolForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory
from guardian.shortcuts import assign_perm
from guardian.decorators import permission_required_or_403


#### GLOBALES
PROYECTOS_USUARIO=[]
"""SE UTILIZA PARA GUARDAR LA LISTA DE ID DE LOS PROYECTOS DEL USUARIO"""
CANTIDAD=1
"""SE UTILIZA PARA GUARDAR LA CANTIDAD DE FASES DE UN PROYECTO"""


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
            registrarAuditoria(request.user,"cambio el estado del proyecto : "+str(p.nombre)+ " a Finalizado")
            return redirect('gestion:listar_proyectos')### VUELVE A LISTAR LOS PROYECTOS DEL USUARIO
        elif(z=="INICIADO"):
            ok=False
            fase= Fase.objects.all()
            IdFase=0
            for i in range(fase.count()):
                if(fase[i].id_Proyecto.id_proyecto==p.id_proyecto):
                    ti = TipoItem.objects.all()
                    IdFase = fase[i].id_Fase
                    for x in range(ti.count()):
                        if(ti[x].fase.id_Fase==fase[i].id_Fase):
                            ok=True
            print(IdFase)
            if(ok==True):
                registrarAuditoria(request.user,"cambio el estado del proyecto : "+str(p.nombre)+ " a Iniciado")
                p.estado=z####### SE ASIGNA ESTADO
                p.save()##### SE GUARDA
                return redirect('gestion:listar_proyectos')### VUELVE A LISTAR LOS PROYECTOS DEL USUARIO

            context = {
                "mensaje":"NO POSEE TIPOS DE ITEM CREE AL MENOS UNO PAARA INICIAR EL PROYECTO",
                "titulo":"FALTA TI",
                "titulo_b1": "Crear TI",
                "boton1":"/crear/TipoItem/"+str(IdFase),
                "titulo_b2":"Volver a proyectos",
                "boton2":"/proyectos/"
            }
            return render(request, 'Error.html', context)
        elif(z=="CANCELADO"):
            registrarAuditoria(request.user,"cambio el estado del proyecto : "+str(p.nombre)+ " a Cancelado")
            p.estado=z####### SE ASIGNA ESTADO
            p.save()##### SE GUARDA
            return redirect('gestion:listar_proyectos')### VUELVE A LISTAR LOS PROYECTOS DEL USUARIO

    context={
        "form":form,
        "estado": p.estado,
        'proyecto':p
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

        CorreoMail(asunto,mensaje,"gerardocabrer@gmail.com")
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
    """MENU PARA LOS USUARIOS DE ACUERDO A SUS ROLES, PARA ADMINISTRADOR DE SISTEMAS,
    GERENTE DE PROYECTO, USUARIO QUE FORMA PARTE DEL SISTEMA Y DEL QUE NO FORMA PARTE"""
    user = request.user
    #return render(request, 'MenuAdminSistema.html')
    if( user.usuario.esta_aprobado):
        if user.has_perm('gestion.es_administrador'):
             return render(request,'MenuAdminSistema.html')
        else:
            return render(request, 'Menu.html')
    else:
        registrarAuditoria(request.user ,'Inicio Menu en espera de aprobacion')
        return render(request, 'MenuEnEspera.html')


def agregarUsuarios(request,pk,nroFase):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    RECIBE EL ID DEL PROYECTO Y MUESTRA LOS USUARIOS QUE PUEDEN SER AÑADIDOS A EL
    """

    user= request.user## USER ACTUAL

    form = Usuario.objects.all()
    registrados = User_Proyecto.objects.all()

    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        #if form.is_valid():
        some_var=request.POST.getlist('checkbox')
        print(some_var)
        for id in some_var:###### SE GUARDAN EN USER_PROYECTOS LAS RELACIONES
            id_user =id
            p = User_Proyecto(user_id= id_user ,proyecto_id= pk,activo= True)
            p.save()

        #form.save()
        return redirect('gestion:crearFase',nroFase)
    else:
        list=[]
        for i in range(form.count()):
            ok = False
            if form[i].esta_aprobado == True and form[i].user.id != user.id:
                ok=True
                for x in range(registrados.count()):
                    if registrados[x].proyecto_id == pk:
                        if form[i].user.id == registrados[x].user_id:
                            ok=False
            if ok:
               list.append(form[i].user.id)

        return render(request, 'agregarUsuarios.html', {'form': form,'list':list,'pk':pk})


def creacionProyecto(request):
    """PLANTILLA DE FORMULARIO PARA LA CREACION DE UN PROYECTO"""

    formProyecto = FormProyecto(request.POST or None)   ######## forms con proyecto

    if formProyecto.is_valid():
        instanceProyecto = formProyecto.save(commit=False)########## impide que se guarde a la BD
        ### NADA QUE TOCAR
        instanceProyecto.save()######## guarda a la BD, en medio se puede manipular el texto

        global CANTIDAD
        cantidad = formProyecto.cleaned_data
        cantidad_fases=cantidad.get("fase")##### PARA WALTER
        CANTIDAD=cantidad_fases-1

        registrarAuditoria(request.user, 'Creo el proyecto: '+ str(instanceProyecto.nombre))

        q = request.user
        z= Proyecto.objects.last()
        id_proyecto = z.id_proyecto ## ID DEL PROYECTO CREADO
        p = User_Proyecto(user_id= q.id ,proyecto_id= id_proyecto,activo= True)
        p.save()

        print(cantidad_fases)
        cantidad_fases=cantidad_fases-1
        print(cantidad_fases)
        return redirect('gestion:agregarUsuarios',id_proyecto,cantidad_fases)

    context ={
        "formProyecto": formProyecto,
    }

    return render(request,'creacionProyecto2.html', context)

def index(request):
    """INICIO DE APLICACION, SOLICITUD DE INICIAR SESION DEL SISTEMA, SOLO SE MUESTRA SI NO SE ESTA REGISTRADO EN EL SSO"""
    user = request.user
    if user.is_authenticated:
        validar_usuario(request.user)
        return redirect('gestion:menu')
    else:
        return render(request,'index.html')

@login_required
def perfil(request):
    """SOLICITUD DE AUTENTICACION PARA MOSTRAR EL PERFIL DEL USUARIO||
    Realiza consultas de los datos del usuario que esta realizando la
    solicitud, y lo envia al html, para asi mostrarselo sus datos de ese usuario"""

    registrarAuditoria(request.user, 'Ingreso en el apartado perfil')
    usuario=Usuario.objects.get(user_id=request.user.id)
    user = request.user
    auth0user = user.social_auth.filter(provider='auth0')[0]
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'estado': usuario.esta_aprobado,
        'picture': auth0user.extra_data['picture'],
    }

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


#jesus
def ver_usuarios_aprobados(request):
    '''Lista todos los usarios aprobados en el sistema '''
    users=Usuario.objects.filter(esta_aprobado=True).exclude(user_id=request.user.id)
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
                    proyectos_user= User_Proyecto.objects.filter(user_id=user.id)
                    print('si esta asociada a un proyecto')
                    print(proyectos_user)
                    for pu in proyectos_user:
                        if pu.activo:
                            print('Esta activo')
                            print(pu.proyecto_id)
                            ban=False
                            break
            if ban:
                print ('ban es true')
                add_permission_admin(user, is_admin)
                add_permission_gerente(user, is_gerente)
                usuario=Usuario.objects.get(user_id=user.id)
                usuario.esta_aprobado=estado
                usuario.save()
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
    fase=Fase.objects.get(id_Fase=fase_id)
    #proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto_id)
    my_form = formset_factory(AtributeForm, extra=cantidad_atributos)
    if request.method == 'POST':
        my_form_set=my_form(request.POST)
        if(my_form_set.is_valid()):
            tipo_item=TipoItem(nombre=nombre_ti,fase_id=fase_id)
            tipo_item.save()
            for form in my_form_set:
                n,o,t=recoge_datos_atributo(form)
                atributo1=Atributo.objects.create(nombre=n,es_obligatorio=o,tipo_dato=t,ti_id=tipo_item.id_ti)
            return redirect('gestion:detalles_Proyecto',pk=fase.id_Proyecto_id)
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
    content_type = ContentType.objects.get_for_model(Usuario)
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

def crearFase(request,nroFase):
    """METODO PARA CREAR FASES"""
    fase = FaseForm(request.POST)
    global CANTIDAD
    cantidad = CANTIDAD
    if fase.is_valid():
        x = Proyecto.objects.last()
        nombreFase = fase.cleaned_data.get("nombre")
        descFase = fase.cleaned_data.get("descripcion")
        z = Fase(nombre=nombreFase,descripcion=descFase,id_Proyecto=x)
        z.save()
        registrarAuditoria(request.user, 'Creo la Fase: '+str(z.nombre)+' en el proyecto: '+ str(x.nombre))
        if nroFase != 0:
            cantidad = cantidad - 1
            CANTIDAD = cantidad

            nroFase=nroFase-1
            return redirect('gestion:crearFase',nroFase)
        else:
            assign_perm('is_gerente', request.user, x)
            return redirect('gestion:menu')

    context = {
    'form': fase
    }
    return render(request, 'crear_fase.html', context)

def listar_auditoria(request):
    """ LISTA LOS REGISTROS DE LA TABLA AUDITORIA """
    auditoria = Auditoria.objects.all()
    context={
        'auditoria':auditoria
    }
    return render(request, 'Auditoria.html', context)


def AggUser(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    MEDIANTE UN PROYECTO EXISTENTE, DA LA POSIBILIDAD DE AÑADIR MAS USUARIOS AL PROYECTO,
    FILTRANDO LOS USUARIOS QUE NO FORMAN PARTE DEL PROYECTO
    """
    registrarAuditoria(request.user, 'Ingreso al apartado de registro de usuarios a un proyecto')
    user= request.user## USER ACTUAL

    form = Usuario.objects.all()
    registrados = User_Proyecto.objects.all()

    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        #if form.is_valid():
        some_var=request.POST.getlist('checkbox')
        print(some_var)

        for id in some_var:###### SE GUARDAN EN USER_PROYECTOS LAS RELACIONES
            id_user =id
            p = User_Proyecto(user_id= id_user ,proyecto_id= pk,activo= True)
            p.save()

        #form.save()
        return redirect('gestion:detalles_Proyecto',pk)
    else:
        list=[]
        for i in range(form.count()):
            ok = False
            if form[i].esta_aprobado == True and form[i].user.id != user.id:
                ok=True
                for x in range(registrados.count()):
                    if registrados[x].proyecto_id == pk:
                        if form[i].user.id == registrados[x].user_id:
                            ok=False
            if ok:
               list.append(form[i].user.id)

        return render(request, 'AggUser.html', {'form': form,'list':list,'pk':pk})


def UsersProyecto(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    LISTA LOS USUARIOS DE UN PROYECTO
    """
    proyecto=Proyecto.objects.get(id_proyecto=pk)
    registrarAuditoria(request.user, 'Ingreso al apartado de registro de usuarios a un proyecto')
    user= request.user## USER ACTUAL
    form = User.objects.all()
    registrados = User_Proyecto.objects.all()
    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        #if form.is_valid():
        some_var=request.POST.getlist('checkbox')
        print(some_var)


        #form.save()
        return redirect('gestion:menu')
    else:
        list=[]
        for i in range(form.count()):
            ok = False
            if form[i].id != user.id: #and form[i].esta_aprobado == True :
                for x in range(registrados.count()):
                    if registrados[x].proyecto_id == pk:
                        if form[i].id == registrados[x].user_id:
                            ok=True
            if ok:
               list.append(form[i].id)

        return render(request, 'UsersProyecto.html', {'form': form,'list':list,'pk':pk,'proyecto':proyecto})


def desvinculacionProyecto(request,pk,pk_user):
    """DESVINCULA UN USUARIO DE UN PROYECTO"""
    instanceUser = User_Proyecto.objects.filter(proyecto_id = pk, user_id = pk_user)
    instanceUser.delete()
    return redirect('gestion:UsersProyecto',pk)

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
    """MUESTRA LAS OPCIONES REALIZABLES SOBRE UN PROYECTO, TAMBIEN MUESTRA LAS FASES DEL MISMO CON SUS
    OPCIONES"""
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
    """METODO PARA CANCELAR UN PROYECTO"""
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
    """MUESTRA LOS DETALLES DE UN PROYECTO"""
    proyecto=Proyecto.objects.get(id_proyecto=pk)
    fases = Fase.objects.filter(id_Proyecto_id=pk)
    contexto={
        'proyecto':proyecto,
        'fases':fases
    }
    return render(request,'opcionesProyecto.html',contexto)

def get_fase_proyecto(request,id_fase):
    """TRAE LA FASE DE UN PROYECTO"""
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
    fase = Fase.objects.get(id_Fase=id_fase)
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
        return redirect('gestion:detalles_Proyecto',pk=fase.id_Proyecto_id)
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
            if(proyecto.user_id==request.user.id):
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

#Parte de Ger
class VerUsersEnEspera(ListView):
    """Vista creada para listar los usuarios que se encuentran
    en espera de ser aprobados dentro del sistema, vista que solo puede ser accedida
    por el administrador del sistema,
    Se especifica el atributos
    -model:donde se asigna el Modelo utilizado
    -template_name: donde se asigna que template estara asignado esta view
    -queryset: Se filtra la lista de usuarios con estado aprobado falso, y es recibido por el template"""
    model = Usuario
    template_name = "ListaUser.html"
    queryset = Usuario.objects.filter(esta_aprobado=False)

    #@method_decorator(permission_required('gestion.es_administrador',raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(VerUsersEnEspera,self).dispatch(request)

class ActualizarUser(UpdateView):
    """Se muestra el perfil del usuario seleccionado, en donde se
    especifican los siguientes atributos:
    """
    model = Usuario
    """    -model: especifa el modelo el cual esta siendo utilizado en la view"""
    form_class = PerfilUserEnEspera
    """    -form_class: especifica el form que sera utilidado dentro del template"""
    template_name = 'UserEnEspera.html'
    """-template_name: donde se asigna que template estara asignado esta view"""
    success_url = reverse_lazy('gestion:listaDeEspera')
    """    -succes_url: es especifica a que direccion se redirigira la view una vez actualizado el objeto dentro del modelo"""
    def get_context_data(self, **kwargs):
        """Se recibe id fecha de registro nombre y email de un usuario, se lo manda al template """
        context = super().get_context_data(**kwargs)
        context['IDUser'] = self.object.id
        context['fecha_registro']=self.object.user.date_joined
        context['nombre']=self.object.user.username
        context['email']=self.object.user.email
        return context
    def post(self, request, *args, **kwargs):
        """Envia un correo al usuario al ser aprobado en el sistema"""
        usuario=Usuario.objects.get(id=self.kwargs['pk'])
        if request.POST["esta_aprobado"] == 'True':
            CorreoMail("Aprobado","Usted fue apobado en el sistema, bienvenido!!",usuario.user.email )
        return super(ActualizarUser, self).post(request, **kwargs)


class CrearRol(CreateView):
    """Se muestra la ventana para la creacion de un nuevo rol dentro de un proyecto, en donde se
    especifican los siguientes atributos:"""
    model = Group
    """    -model: especifa el modelo el cual esta siendo utilizado en la view"""
    form_class = RolForm
    """    -form_class: especifica el form que sera utilidado dentro del template"""
    template_name = "CrearRol.html"
    """    -template_name: donde se asigna que template estara asignado esta view"""
    success_url = reverse_lazy("gestion:menu")
    """-succes_url: es especifica a que direccion se redirigira la view una vez actualizado el objeto dentro del modelo"""
    def post(self, request, *args, **kwargs):
        """    La funcion redeclara es la de post, en donde se realiza una modificacion del nombre declarado
            para la creacion, agregandole el id del proyecto perteneciente delate, esto para el reconocimiento
            del proyecto pertenciente de este Rol a crear"""

        request.POST = request.POST.copy()
        request.POST['name']  = self.kwargs['proyecto']+'_'+request.POST['name']
        return super(CrearRol,self).post(request,**kwargs)

def validar_usuario(user):
    """Valida al usuario al inicio del sistema, el primer usuario se le asigna el rol de administrador del sistema
    se le agrega el estado aprobado"""
    if (User.objects.count() == 2):
        add_permission_admin(user, True)
        Usuario.objects.create(esta_aprobado=True,user_id=user.id)

    usuario=Usuario.objects.filter(user_id=user.id).exists()
    if not usuario:
        Usuario.objects.create(esta_aprobado=False,user_id=user.id)

class ModificarRol(UpdateView):
    """Se muestra el rol seleccionado dentro del proyecto
    """
    model = Group
    """ -model: especifa el modelo el cual esta siendo utilizado en la view"""
    form_class = RolForm
    """-form_class: especifica el form que sera utilidado dentro del template"""
    template_name = 'CrearRol.html'
    """-template_name: donde se asigna que template estara asignado esta view"""
    success_url = reverse_lazy('gestion:menu')
    """-succes_url: es especifica a que direccion se redirigira la view una vez actualizado el objeto dentro del modelo"""
def listar_tipo_item(request,id_proyecto):
    """Lista los tipos de item asociado a un proyecto"""
    fases=Fase.objects.filter(id_Proyecto_id=id_proyecto)
    tipoItem=[]
    for fase in fases:
        tipoItem += TipoItem.objects.filter(fase_id=fase.id_Fase)

    print(tipoItem)
    contexto={
        'TipoItem':tipoItem
    }
    return render (request,'listarTipoItem.html',contexto)


class VerRoles(ListView):
    """Vista creada para listar los roles que se encuentra dentro de un proyecto
    """
    model = Group
    """    -model:donde se asigna el Modelo utilizado"""
    template_name = "misRoles.html"
    """    -template_name: donde se asigna que template estara asignado esta view"""
    def get_context_data(self, **kwargs):
        """recibe el id del proyecto y se listan los roles cone se id"""
        context = super().get_context_data(**kwargs)
        miid = self.kwargs['proyecto']

        grupos = Group.objects.all()
        grupList = []
        for grupo in grupos:
            numero, divisor, nombre = grupo.name.partition('_')
            if (int(numero) == miid):
                grupList += [{'grupo':grupo,'nombre':nombre}]

        context['listGroup'] = grupList
        context['idProyecto'] = miid
        return context

def crearItem(request,Faseid):

    form= FormItem(request.POST)
    if form.is_valid():
        form.save(commit=False)

        datosFormulario= form.cleaned_data
        fase= Fase.objects.filter(id_Fase=Faseid)

        item=Item(nombre=datosFormulario.get('nombre'),descripcion=datosFormulario.get('descripcion'),costo=datosFormulario.get('costo'),fase=fase[0])
        item.save()
        return redirect('gestion:agg_listar_tipo_item',Faseid)
    contexto={
        "form":form
    }
    return render (request,'Item.html',contexto)

def agg_listar_tipo_item(request,Fase):
    """Lista los tipos de item asociado a un proyecto"""

    if request.method == 'POST':
        x=request.POST.get('ti')

        item=Item.objects.last()
        tipoItem2 = TipoItem.objects.filter(nombre=x,fase_id=Fase)
        item.ti =tipoItem2[0]
        item.save()

        return redirect('gestion:aggAtributos',tipoItem2[0].id_ti)

    tipoItem = TipoItem.objects.filter(fase_id=Fase)
    contexto={
        'TipoItem':tipoItem
    }
    return render (request,'aggTI.html',contexto)


def aggAtributos(request,idTI):
    atributos= Atributo.objects.filter(ti_id=idTI)

    if request.method == 'POST':

        x = request.POST.getlist('valor')
        print(x)

        item=Item.objects.last()

        for i in x:
#            print(i)
            p = Atributo_Item(idAtributoTI=idTI,id_item=item,valor=i)
            p.save()


        itemID=Item.objects.last()
        ti=TipoItem.objects.get(id_ti=idTI)
        return redirect('gestion:relacionarItem',ti.fase.id_Proyecto.id_proyecto,itemID.id_item)

    contexto={
        'atributos':atributos
    }
    return render (request,'aggAtributos.html',contexto)



def relacionarItem(request,id_proyecto,id_item):
    """
    RECIBE EL ID DEL PROYECTO Y MUESTRA LOS USUARIOS QUE PUEDEN SER AÑADIDOS A EL
    """
    items = Item.objects.filter(actual=True)

    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        some_var=request.POST.getlist('checkbox')
        print(some_var)
        for id in some_var:###### SE GUARDAN EN USER_PROYECTOS LAS RELACIONES
            p = Relacion(inicio_item=id_item,fin_item=id)
            p.save()

        version=Versiones(id_Version=1,id_item=id_item)
        version.save()

        return redirect('gestion:menu')
    else:
        list=[]
        for i in range(items.count()):###todos los items del proyecto
            if items[i].fase.id_Proyecto.id_proyecto == id_proyecto and id_item !=items[i].id_item:
               list.append(items[i].id_item)

        print(list)
        return render(request, 'relacionarItem.html', {'form': items,'list':list})
