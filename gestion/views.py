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
from .models import Proyecto,TipoItem,Atributo,Item,Fase,Atributo_Item,Relacion,Versiones,Comite
from .forms import FormProyecto,TipoItemForm,AtributeForm,RolForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory
from django.forms.models import modelformset_factory
from guardian.shortcuts import assign_perm
from guardian.decorators import permission_required_or_403
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
import webbrowser
import dropbox

#### GLOBALES
PROYECTOS_USUARIO=[]
"""SE UTILIZA PARA GUARDAR LA LISTA DE ID DE LOS PROYECTOS DEL USUARIO"""
CANTIDAD=1
"""SE UTILIZA PARA GUARDAR LA CANTIDAD DE FASES DE UN PROYECTO"""

"""
datos de dropbox
gestionitems.fpuna@gmail.com    
GestionItem20202
https://josevc93.github.io/python/Dropbox-y-python/
"""
TOKEN="4BJ-WaMHHDAAAAAAAAAADHjatAzpvWFcLRnLg-HxMI5mjihNv0ib_E3rTAV0MVbf"
"""TOKEN DE DROPBOX PARA REALIZAR LA CONEXION"""


#RUBEN
def estadoProyecto(request,pk):
    """
    RECIBE EL ID DEL PROYECTO A CAMBIAR SU ESTADO Y EL ESTADO NUEVO MEDIANTE EL POST,
    VALIDA CADA UNO DE LOS ESTADOS:
    INICIADO: VALIDA EL COMITE DE CAMBIO SI ES MAYOR O IGUAL A 3 USUARIOS, TAMBIEN VALIDA
    QUE EL PROYECTO POSEA AL MENOS UN TIPO DE ITEM.
    FINALIZADO: VALIDA QUE TODAS LAS RESTRICCIONES DEL PROYECTO SEAN CUMPLIDAS.
    CANCELADO: CANCELA EL PROYECTO SIN NINGUNA VALIDACION YA QUE EL PROYECTO SE PUEDE CANCELAR EN CUALQUIER ESTADO
    MENOS CUANDO ESTE FINALIZADO.

    :param request:
    :param pk: ID DEL PROYECTO EN EL CUAL SE CAMBIARA EL ESTADO
    :return: ESTADOPROYECTO.HTML
    """

    #if(request.user.has_perm('id_gerente')):----------------------------------------------

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

            cantidad=0
            try:
                comite = Comite.objects.filter(id_proyecto=pk)
                cantidad = comite.count()
            except:
                comite = None
                cantidad =0

            if(cantidad < 3):
                comite=None

            if (comite == None):
                context = {
                    "mensaje": "EL NUMERO DE USUARIOS EN EL COMITE DEBE DE SER IMPAR Y MAYOR A UNO",
                    "titulo": "ERROR AL SELECCIONAR",
                    "titulo_b1": "SELECCIONAR USUARIOS",
                    "boton1": "/AggComite/" + str(pk),
                    "titulo_b2": "CANCELAR",
                    "boton2": "/detallesProyecto/" + str(pk),
                }
                return render(request, 'Error.html', context)

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
            if(p.estado != 'FINALIZADO'):
                registrarAuditoria(request.user,"cambio el estado del proyecto : "+str(p.nombre)+ " a Cancelado")
                p.estado=z####### SE ASIGNA ESTADO
                p.save()##### SE GUARDA
                return redirect('gestion:listar_proyectos')### VUELVE A LISTAR LOS PROYECTOS DEL USUARIO
            else:
                context = {
                    "mensaje": "EL PROYECTO SE ENCUENTRA FINALIZADO POR ENDE NO SE PUEDE CANCELAR",
                    "titulo": "PROYECTO YA SE FINALIZO",
                    "titulo_b1": "SALIR",
                    "boton1": "/proyectos/" ,
                    "titulo_b2": "",
                    "boton2": ""
                }
                return render(request, 'Error.html', context)

    context={
        "form":form,
        "estado": p.estado,
        'proyecto':p
    }
    return render(request, 'Menu/estado_proyecto.html',context)
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'Editar estado')

def errorPermiso(permiso):
    """
    MENSAJE DE ERROR CUANDO NO SE POSEE EL PERMISO
    :param permiso: PERMISO QUE LE HACE FALTA AL USUARIO
    :return: ERROR.HTML
    """

    context = {
        "mensaje": "NO TIENE EL PERMISO CORRESPONDIENTE NO PUEDE REALIZAR LA ACCION",
        "titulo": "SIN EL PERMISO DE : "+ str(permiso),
        "titulo_b1": "SALIR",
        "boton1": "/menu/",
        "titulo_b2": "",
        "boton2": "",
    }
    return render(request, 'Error.html', context)


#RUBEN
def registrarAuditoria(user,accion):
    """FUNCION QUE REGISTRA EN LA  TABLA AUDITORIA LO QUE SE REALIZA EN EL SISTEMA"""
    showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    p = Auditoria(usuario= user,fecha=showtime, accion=accion)###### FALTA ARREGLAR USER
    p.save()

def registrarAuditoriaProyecto(user,accion,id_proyecto,proyecto,fase):
    """
    FUNCION QUE REGISTRA EN LA  TABLA AUDITORIA LO QUE SE REALIZA EN UN PROYECTO EN ESPECIFICO
    :param user: USUARIO ACTUAL
    :param accion: ACCION REALIZADA
    :param id_proyecto: ID DEL PROYECTO EN EL CUAL REALIZO LA ACCION
    :param proyecto: PROYECTO
    :param fase: FASE DEL PROYECTO

    """

    showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    p = Auditoria(usuario= user,fecha=showtime, accion=accion,id_proyecto=id_proyecto,proyecto=proyecto,fase=fase)###### FALTA ARREGLAR USER
    p.save()

#RUBEN
def CorreoMail(asunto,mensaje,correo):
    """
    FUNCION QUE RECIBE UN ASUNTO, MENSAJE Y UN CORRREO ELECTRONICO AL CUAL SE LE ENVIA UN CORREO
    ELECTRONICO DE ACUERDO A UNA ACCION
    :param asunto: ASUNTO DEL MENSAJE
    :param mensaje: MENSAJE A ENVIAR
    :param correo: EMAIL
    """

    mail=EmailMessage(asunto,mensaje,to={correo})
    mail.send()
#RUBEN
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
        context = {
            "mensaje": "GRACIAS POR UTILIZAR NUESTRO SISTEMA! :)",
            "titulo": "MENSAJE ENVIADO",
            "titulo_b1": "SALIR",
            "boton1": "/menu/",
            "titulo_b2": "",
            "boton2": "",
        }
        return render(request, 'Error.html', context)

    context={
        "form":form,
    }
    registrarAuditoria(request.user,'Ingreso en el apartado contactos')
    return render(request,'Menu/contactos.html', context)

#RUBEN
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
import time
from datetime import datetime

def menu(request):
    """MENU PARA LOS USUARIOS DE ACUERDO A SUS ROLES, PARA ADMINISTRADOR DE SISTEMAS,
    GERENTE DE PROYECTO, USUARIO QUE FORMA PARTE DEL SISTEMA Y DEL QUE NO FORMA PARTE"""
    user = request.user
    if( user.usuario.esta_aprobado):
        if user.has_perm('gestion.es_administrador'):
            return render(request,'Menu/MenuAdministrador.html')
        else:
            return render(request, 'Menu/Menu.html')
    else:
        registrarAuditoria(request.user ,'Inicio Menu en espera de aprobacion')
        return render(request, 'Menu/MenuEnEspera.html')

#RUBEN
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

        return render(request, 'proyectos/agregarUsuarios.html', {'form': form,'list':list,'pk':pk})

#RUBEN
def creacionProyecto(request):
    """
    MUESTRA FORMULARIO PARA CREAR UN PROYECTO EN DONDE SE VALIDA, NOMBRE, DESCRIPCION Y CANTIDAD DE FASES
    UNA VEZ COMPLETADO LOS MISMOS, SE AÑADE EN LA TABLA USER_PROYECTOS AL GERENTE EL CUAL CREO EL MISMO Y SE
    GUARDA EN LA BASE DE DATOS EL PROYECTO Y REEDIRIGE A  CREACION DE FASES MOSTRANDO LAS FASES A CREARSE

    :param request:
    :return: CREACIONPROYECTO2.HTML
    """
    #if(request.user.has_perm('id_gerente')):----------------------------------------------

    formProyecto = FormProyecto(request.POST or None)   ######## forms con proyecto
    if formProyecto.is_valid():
        instanceProyecto = formProyecto.save(commit=False)########## impide que se guarde a la BD
        ### NADA QUE TOCAR
        cantidad = request.POST.get("fase")

        cantidad_fases=int(cantidad[0])##### PARA WALTER

        print(cantidad_fases)
        if(cantidad_fases<=0):
            context = {
                "mensaje": "LA FASE DEBE SER MAYOR A 1",
                "titulo": "ERROR EN FASE",
                "titulo_b2": "INTENTAR DE NUEVO",
                "boton2": "/creacionProyecto/",
                "titulo_b1": "SALIR",
                "boton1": "/menu/",
            }
            return render(request, "Error.html", context)

        instanceProyecto.save()######## guarda a la BD, en medio se puede manipular el texto

        global CANTIDAD


        CANTIDAD=cantidad_fases-1


        q = request.user
        z= Proyecto.objects.last()
        id_proyecto = z.id_proyecto ## ID DEL PROYECTO CREADO
        p = User_Proyecto(user_id= q.id ,proyecto_id= id_proyecto,activo= True)
        p.save()

        registrarAuditoriaProyecto(request.user, 'Creo el proyecto',z.id_proyecto,instanceProyecto.nombre,'')

        cantidad_fases=cantidad_fases-1
        return redirect('gestion:agregarUsuarios',id_proyecto,cantidad_fases)

    context ={
        "formProyecto": formProyecto,
    }

    return render(request,'proyectos/crear_proyecto.html', context)
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'No es gerente')

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

    return render(request, 'Menu/perfil.html', {
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
    return render(request,'Menu/usuariosAprobados.html',context)

def get_user(request,pk):
    ''' Sirve para poder asignar o sacar los permisos es_gerente , es_administrador
        y cambiar el estado de un usario en especifico
    '''
    user_active=False
    if( request.method == 'POST' ):
        user = User.objects.get(id=pk)

        is_admin, is_gerente, estado = recoger_datos_usuario_settings(request.POST.copy())
        print(is_admin,is_gerente,estado)
        ban = True
        if estado == 'False':  # si el estado es falso
            print('estado Falso')
            if User_Proyecto.objects.filter(
                    user_id=user.id).exists():  # si el usuario no esta asociado a ningun proyecto
                proyectos_user = User_Proyecto.objects.filter(user_id=user.id)
                print('si esta asociada a un proyecto')
                print(proyectos_user)
                for pu in proyectos_user:
                    if pu.activo:
                        print('Esta activo')
                        print(pu.proyecto_id)
                        ban = False
                        break
        if ban:
            print('ban es true')
            add_permission_admin(user, is_admin)
            add_permission_gerente(user, is_gerente)
            usuario = Usuario.objects.get(user_id=user.id)
            usuario.esta_aprobado = estado
            usuario.save()
        else:
            contexto = {
                'mesanje_error': 'El usuario esta activo en un proyecto por lo tanto no puedes desactivarlo, para hacerlo deben de darle de baja en el proyecto que en donde esta asociado   '

            }
            return render(request, 'error.html', contexto)
        return redirect('gestion:ver_usuarios_aprobados')
    else:
        usuario=User.objects.get(id=pk)
        banAdmin=usuario.has_perm('gestion.es_administrador')
        banGerente=usuario.has_perm('gestion.is_gerente')
        print(banAdmin,banGerente)
        form=SettingsUserFormJesus()
        context = {
            'user': usuario,
            'form':form,
            'banAdmin':str(banAdmin),
            'banGerente':str(banGerente)
        }
        return render(request,"Menu/perfilUsuario.html",context)

def tipo_item_views_create(request,id_fase):
    '''Sirve para crear un tipo de item,en una fase en especifica'''
    if request.method == "POST":
        my_form=TipoItemForm(request.POST)
        if(my_form.is_valid()):
           nombre_ti,cantidad_atributos_ti=recoger_datos_tipo_item(my_form)
           if( cantidad_atributos_ti==None or cantidad_atributos_ti<=0):
               context = {
                   "mensaje": "La cantidad de atributos del tipo de item debe de ser >=0 ",
                   "titulo": "Cantidad Atributo erronea",
                   "titulo_b2": "Intentalo de vuelta",
                   "boton2": "",
               }
               return render(request, "Error.html", context)
           return redirect('gestion:add_atribute',nombre_ti=nombre_ti,cantidad_atributos=cantidad_atributos_ti,fase_id=id_fase)
    else:
        my_form= TipoItemForm()
        fase=Fase.objects.get(id_Fase=id_fase)
        proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto_id)
        context={
            'tipo_item_form': my_form,
            'proyectos':proyecto
           }
        return render(request, 'proyectos/crear_tipo_item.html', context)
#Vistas agregadas por jesus

def add_atribute(request,nombre_ti,cantidad_atributos,fase_id):
    ''' Sirve para poder crear un nuevo atributo, asociando ese atributo a un tipo de item'''
    cantidad_atributos=int(cantidad_atributos)
    fase_id=int(fase_id)
    fase=Fase.objects.get(id_Fase=fase_id)
    #proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto_id)
    my_form = formset_factory(AtributeForm, extra=cantidad_atributos)
    if request.method == 'POST':
        my_form_set=my_form(request.POST)
        if(my_form_set.is_valid()):
            print('aca imprimo')
            if validar_datos_form_atributo(my_form_set):
                tipo_item=TipoItem(nombre=nombre_ti,fase_id=fase_id)
                tipo_item.save()
                for form in my_form_set:
                    n,o,t=recoge_datos_atributo(form)
                    atributo1=Atributo.objects.create(nombre=n,es_obligatorio=o,tipo_dato=t,ti_id=tipo_item.id_ti)
                return redirect('gestion:detalles_Proyecto',pk=fase.id_Proyecto_id)
            else:
                context = {
                    "mensaje": "Debes de completar todos los campos del formulario",
                    "titulo": "Error al cargar el formulario de atributo ",
                    "titulo_b2": "Intentalo de vuelta",
                    "boton2": "",
                }
                return render(request, "Error.html", context)
    else:
        contexto={'formset':my_form,
                 'cant_atributos': list(range(1,cantidad_atributos+1)),
                'proyectos':fase.id_Proyecto
                }
        return render(request,'proyectos/crear_atributo.html',contexto)

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
    print('aca imprime')
    print('aca imprime el form ',form)
    is_admin = form.get('admin')
    is_gerente = form.get('gerente')
    estado = form.get('estado')
    if(is_admin==None):
        is_admin=False
    if is_gerente==None:
        is_gerente=False
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
    #if(request.user.has_perm('id_gerente')):---------------------------------------------
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
            add_permission_gerente(request.user,False)
            return redirect('gestion:menu')

    context = {
    'form': fase
    }
    return render(request, 'proyectos/crear_fase.html', context)
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'No es gerente')

#RUBEN
def listar_auditoria(request):
    """ LISTA LOS REGISTROS DE LA TABLA AUDITORIA PARA EL SISTEMA"""
    auditoria = Auditoria.objects.all()
    proyectos=Proyecto.objects.get(id_proyecto=1)

    context={
        'auditoria':auditoria,
        'proyectos': proyectos

    }
    return render(request, 'Menu/auditoriaSistema.html', context)

def auditoriaProyecto(request,pk):
    """
    LISTA LOS REGISTROS DE LA TABLA AUDITORIA PARA UN PROYECTO EN ESPECIFICO
    :param request:
    :param pk: ID DEL PROYECTO DEL CUAL SE LISTARA LA AUDIRORIA
    :return: AUDITORIA.HTML
    """

    auditoria = Auditoria.objects.filter(id_proyecto=pk)
    proyectos=Proyecto.objects.get(id_proyecto=pk)
    context={
        'auditoria':auditoria,
        'proyectos':proyectos
    }
    return render(request, 'proyectos/ver_auditoria.html', context)

#RUBEN
def AggUser(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    MEDIANTE UN PROYECTO EXISTENTE, DA LA POSIBILIDAD DE AÑADIR MAS USUARIOS AL PROYECTO,
    FILTRANDO LOS USUARIOS QUE NO FORMAN PARTE DEL PROYECTO

    :param request:
    :param pk: ID DEL PROYECTO
    :return: AGGUSER.HTML
    """
    #if(request.user.has_perm('is_gerente')):--------------------------------------------------------
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
            proyectos=Proyecto.objects.get(id_proyecto=pk)
        return render(request, 'proyectos/agg_usuario_proyecto.html', {'form': form,'list':list,'pk':pk,"proyectos":proyectos})
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'Agregar usuarios al proyecto')

#RUBEN
def UsersProyecto(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    LISTA LOS USUARIOS DE UN PROYECTO

    :param request:
    :param pk: ID DEL PROYECTO DEL CUAL SE LISTARAN LOS USUARIOS DEL MISMO
    :return: USERSPROYECTO.HTML
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

        return render(request, 'proyectos/usuarios_proyectos.html', {'form': form,'list':list,'pk':pk,'proyectos':proyecto})

#RUBEN
def desvinculacionProyecto(request,pk,pk_user):
    """
    DESVINCULA UN USUARIO DE UN PROYECTO
    :param request:
    :param pk: ID DEL PROYECTO DEL CUAL DESVINCULAR
    :param pk_user: ID DEL USUARIO AL CUAL DESVINCULAR
    :return:
    """
    try:
        usersComite = Comite.objects.filter(id_proyecto=pk)
    except:
        usersComite = None

    if usersComite!=None:
        for id in usersComite:
            usuario=User.objects.get(id=id.id_user)
            if(usuario.id == pk_user ):
                context = {
                    "mensaje": "EL USUARIO PERTENECE AL COMITE DE CAMBIO POR ENDE NO PODRA DESVINCULARLO DEL PROYECTO, YA QUE LA CANTIDAD DE USUARIOS DEL COMITE QUEDARIA PAR, FAVOR DESVINCULAR DEL COMITE Y LUEGO DEL PROYECTO",
                    "titulo": "EL USUARIO ES DEL COMITE DE CAMBIO",
                    "titulo_b1": "",
                    "boton1": "",
                    "titulo_b2": "SALIR",
                    "boton2": "/detallesProyecto/" + str(pk),
                }
                return render(request, 'Error.html', context)

    #if(request.user.has_perm('is_gerente')):--------------------------------------
    instanceUser = User_Proyecto.objects.filter(proyecto_id = pk, user_id = pk_user)
    instanceUser.delete()
    return redirect('gestion:UsersProyecto',pk)

#RUBEN
def listar_proyectos(request):
    """
    LISTA LOS PROYECTOS DEL USUARIO
    :param request:
    :return: VERPROYECTOS.HTML
    """
    proyectos = Proyecto.objects.all()
    PROYECTOS_USUARIO= CantProyectos(request)
    cant = len(PROYECTOS_USUARIO)
    context={
        'proyectos':proyectos,###### TODOS LOS PROYECTOS
        'list': PROYECTOS_USUARIO,##PROYECTOS DEL USUARIO LOS CUAL SE DEBE MOSTRAR, SOLO ID
        'cant': cant####CANTIDAD DE PROYECTOS QUE POSEE
    }
    return render(request, 'Menu/listar_proyectos.html', context)
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'Desvincular usuario del proyecto')

from django.core import serializers

#RUBEN
def detallesProyecto(request,pk):
    """
    MUESTRA LAS OPCIONES REALIZABLES SOBRE UN PROYECTO, TAMBIEN MUESTRA LAS FASES DEL MISMO CON SUS
    OPCIONES
    :param request:
    :param pk: ID DEL PROYECTO DEL CUAL DE LISTARA SUS DETALLES
    :return: DETALLESPROYECTO.HTML
    """

    proyectos = Proyecto.objects.get(id_proyecto=pk)
    fases= Fase.objects.all()

    context={
        "proyectos":proyectos,
        "fases":fases,
    }
    return render(request, 'proyectos/detalles_proyecto.html', context)

#RUBEN
def detallesFase(request,idFase):
    """
    LISTA LOS ITEMS QUE PERTENECEN A LA FASE Y LAS OPCIONES DE LOS ITEM
    :param request:
    :param idFase: ID DE LA FASE LA CUAL DE DETALLARA
    :return: DETALLESFASE.HTML
    """
    fases = Fase.objects.get(id_Fase=idFase)
    proyectos= Proyecto.objects.get(id_proyecto=fases.id_Proyecto.id_proyecto)
    items=Item.objects.filter(fase=fases)

    context={
        "proyectos":proyectos,
        "fases":fases,
        "items":items,
    }
    return render(request, 'proyectos/detalles_fase.html', context)

def listar_relaciones(request,idItem):
    """
    LISTA LAS RELACIONES DE UN ITEM EN ESPECIFICO MEDIANTE EL ID DEL ITEM

    :param request:
    :param idItem: ID DEL ITEM DEL CUAL SE LISTARAN SUS RELACIONES
    :return: LISTAR_RELACIONES.HTML
    """
    relaciones= Relacion.objects.filter()
    print(relaciones)
    item=Item.objects.all()
    itemActual=Item.objects.get(id_item=idItem)
    ### falta desvincular relacion o agregar nueva y cambiar version

    context={
        "relaciones":relaciones,
        "item":item,
        "itemActual":itemActual,
        'proyectos':itemActual.fase.id_Proyecto
    }
    return render(request, 'items/listar_relaciones.html', context)

def listar_atributos(request,idAtributoTI,id_item):
    """
    MEDIANTE EL ID DEL PROYECTO Y EL ID DEL TI DEL ITEM SE LISTAN LOS ATRIBUTOS DEL TI CON LOS
    VALORES QUE SE GUARDARON EN EL ITEM

    :param request:
    :param idAtributoTI: ID DEL ATRIBUTO DEL ITEM
    :param id_item: ID DEL ITEM DEL CUAL SE LISTARA SUS ATRIBUTOS
    :return: LISTAR_ATRIBUTOS.HTML
    """
    atributos = Atributo_Item.objects.filter(id_item=id_item)
    TI=TipoItem.objects.get(id_ti=idAtributoTI)
    atributo= Atributo.objects.filter(ti=TI)
    itemActual=Item.objects.get(id_item=id_item)
    if(request.method=='POST'):
        ###### FALTA ARREGLAR PARA QUE FUNCIONE CON VERSIONES
        print("falta desvincular relacion o agregar nueva y cambiar version")

    ### falta desvincular relacion o agregar nueva y cambiar version

    context = {
        "atributos":atributos,
        "atributo":atributo,
        'proyectos': itemActual.fase.id_Proyecto,
        'item':itemActual
    }
    return render(request, 'items/listar_atributos.html', context)

#RUBEN
def proyectoCancelado(request):
    """METODO PARA CANCELAR UN PROYECTO"""
    #if(request.user.has_perm('is_gerente')):------------------------------------------------
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
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'No es gerente')

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
        print(some_var)
        for id in some_var:
            print (id_fase)
            print (id)
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
        list_poyecto_tipo_item=[]
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
                        list_tipo_item_a_importar += [{
                                                    'ti':ti,
                                                    'proyecto':Proyecto.objects.get(id_proyecto=proyecto.proyecto_id)
                                                     }]

        print(list_tipo_item_a_importar)
        fase=Fase.objects.get(id_Fase=id_fase)
        proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto_id)
        contexto={
            'tipoItems':list_tipo_item_a_importar,
            'proyectos':proyecto
        }
        return render(request,'proyectos/listaTipoItem.html',contexto)

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
    template_name = "Menu/ListaUser.html"
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
    template_name = 'Menu/UserEnEspera.html'
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
    template_name = "proyectos/CrearRol.html"
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
    template_name = 'proyectos/CrearRol.html'
    """-template_name: donde se asigna que template estara asignado esta view"""
    success_url = reverse_lazy('gestion:menu')
    """-succes_url: es especifica a que direccion se redirigira la view una vez actualizado el objeto dentro del modelo"""
def listar_tipo_item(request,id_proyecto):
    """Lista los tipos de item asociado a un proyecto"""
    fases=Fase.objects.filter(id_Proyecto_id=id_proyecto)
    proyectos=Proyecto.objects.get(id_proyecto=id_proyecto)
    tipoItem=[]

    for fase in fases:
        tipoItem += [{ 'fase':fase,
                    'ti':TipoItem.objects.filter(fase_id=fase.id_Fase)
        }]

    print(tipoItem)
    contexto={
        'proyectos':Proyecto.objects.get(id_proyecto=id_proyecto),
        'TipoItem':tipoItem
    }
    return render (request,'proyectos/listarTipoItem.html',contexto)

class VerRoles(ListView):
    """Vista creada para listar los roles que se encuentra dentro de un proyecto
    """
    model = Group
    """    -model:donde se asigna el Modelo utilizado"""
    template_name = "proyectos/misRoles.html"
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

        context['proyectos'] = Proyecto.objects.get(id_proyecto=miid)

        context['listGroup'] = grupList
        context['idProyecto'] = miid
        return context
#RUBEN
def crearItem(request,Faseid):
    """
    SE CREA UN ITEM CON EL FORM QUE CONTIENE EL NOMBRE, DESCRIPCION, COSTO, LO UNICO QUE NECESITA ES EL IDFASE AL CUAL VA A PERTENECER EL ITEM
    LUEGO DE CREAR, SE GUARDA LO COMPLETADO CON TODOS LOS CAMPOS OBLIGATORIOS, LUEGO REDIRIGE EN UNA VENTANA EN LA CUAL
    MUESTRA TODOS LOS TIPOS DE ITEMS DE DICHA FASE EN LA CUAL PERTENECE EL ITEM Y SE LE PASA EL ID DE LA FASE EN LA QUE SE ENCUENTRA
    EL ITEM
    :param request:
    :param Faseid: ID DE LA FASE EN LA QUE SE CREARA EL ITEM
    :return: ITEM.HTML
    """

    #if(request.user.has_perm('crear_item'):----------------------------------------------------

    fase=Fase.objects.get(id_Fase=Faseid)
    proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto.id_proyecto)
    fases=Fase.objects.filter(id_Proyecto=proyecto)
    cont = 0

    if(proyecto.estado == "INICIADO"):
        context = {
            "mensaje": "EL PROYECTO NO SE ENCUENTRA INICIADO POR ENDE NO SE PUEDE CREAR ITEMS AUN, FAVOR CAMBIE SU ESTADO A INICIADO SI DESEA REALIZAR ESTA ACCION, ESTADO ACTUAL DEL PROYECTO: "+str(proyecto.estado),
            "titulo": "PROYECTO NO INICIADO",
            "titulo_b1": "",
            "boton1": "",
            "titulo_b2": "VOLVER A DETALLES DE LA FASE",
            "boton2": "/detallesFase/" + str(Faseid),
        }
        return render(request, 'Error.html', context)

    if( fases.count() != 1):#si no es de la primera fase
        for faseSIG in reversed(fases):
            cont += 1
            if(faseSIG==fase):#se verifica que fase es
                print("la fase es la nro: ",cont)
                break
    if(cont != 1 ):# si no es de la primera fase valida si hay items en la fase anterior
        item_fase=Item.objects.filter(fase=fase.id_Fase-1)
        print(item_fase)
        if(item_fase.count() == 0):
            print("error")
            context = {
                "mensaje": "LA FASE ANTERIOR NO CONTIENE ITEMS POR ENDE NO PODRA RELACIONAR CON LA PRIMERA FASE, CREE ITEM EN LA FASE ANTERIOR A ESTA Y LUEGO INTENTE NUEVAMENTE",
                "titulo": "NO HAY ITEMS EN LA FASE ANTERIOR",
                "titulo_b1": "",
                "boton1": "",
                "titulo_b2": "VOLVER A DETALLES DE LA FASE",
                "boton2": "/detallesFase/"+str(Faseid),
            }
            return render(request, 'Error.html', context)
        else:
            print("no hay error")
    else:
        print("es la primera fase")

    form= FormItem(request.POST)
    if form.is_valid():
        form.save(commit=False)

        datosFormulario= form.cleaned_data
        fase= Fase.objects.get(id_Fase=Faseid)
        print("fase :",fase.id_Fase)
        item=Item(nombre=datosFormulario.get('nombre'),descripcion=datosFormulario.get('descripcion'),costo=datosFormulario.get('costo'),fase=fase)

        try:
            ti = TipoItem.objects.filter(fase=fase)
        except:
            ti = None
        print(ti.count())

        if (ti==None or ti.count()==0 ):# muestra mensaje de error si no hay TI no se puede crear item
            context = {
                "mensaje": "LA FASE NO CONTIENE NINGUN TI Y  UN ITEM NECESARIAMENTE REQUIERE UNA, ASI QUE CREELA E INTENTE NUEVAMENTE"": ",
                "titulo": "NO HAY TIPOS DE ITEM",
                "titulo_b1": "AÑADE TI A LA FASE",
                "boton1": "/crear/TipoItem/"+str(Faseid) ,
                "titulo_b2": "VOLVER A DETALLES DE LA FASE",
                "boton2": "/detallesFase/"+str(Faseid),
            }
            return render(request, 'Error.html', context)
        item.save()
        return redirect('gestion:agg_listar_tipo_item',Faseid)
    contexto={
        "form":form
    }
    return render (request,'items/Item.html',contexto)
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'Crear Item')

#RUBEN
def agg_listar_tipo_item(request,Fase):
    """
    LISTA LOS TIPOS DE ITEMS DE UNA FASE EN ESPECIFICA, RECIBE EL ID DE LA FASE, AL SELECCIONAR EL TI SE GUARDA EN EL ITEM
    CORRESPONDIENTE Y SE REDIRIGE A UNA VENTANA EN LA QUE SE CARGAN LOS ATRIBUTOS DE DICHO TI SELECCIONADO
    :param request:
    :param Fase: ID DE LA FASE DEL CUAL DEBE LISTAR LOS TI
    :return: AGGTI.HTML
    """

    #if(request.user.has_perm('crear_item')):----------------------------------------------------

    if request.method == 'POST':
        x=request.POST.get('ti')
        item=Item.objects.last()
        tipoItem2 = TipoItem.objects.filter(nombre=x,fase_id=Fase)
        print(tipoItem2)
        item.ti =tipoItem2[0]
        item.save()

        return redirect('gestion:aggAtributos',tipoItem2[0].id_ti)
    tipoItem = TipoItem.objects.filter(fase_id=Fase)
    for i in tipoItem:
        print(i.nombre)
    contexto={
        'TipoItem':tipoItem

    }
    return render (request,'items/aggTI.html',contexto)
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'Crear Item')

#RUBEN
import os
def aggAtributos(request,idTI):
    """
    SE LISTAN LOS ATRIBUTOS DEL TI SELECCIONADO, SE AGREGA UN CAMPO VALOR EN DONDE SE DEBERA DE INGRESAR EL TIPO DE VALOR
    DE DICHO ATRIBUTO, SE VALIDA SI ES OBLIGATORIO Y MUESTRA MENSAJE DE ERROR SI ESTA VACIO EL CAMPO Y ES OBLIGATORIO,
    SI CUMPLIO CON LA RESTRICCION DE OBLIGATORIEDAD REDIRIGE A LA VENTANA DE RELACIONES PARA DICHO ITEM
    :param request:
    :param idTI: ID DEL TI SELECCIONADO POR EL USUARIO
    :return: REDIRIGE AL TEMPLATE AGGATRIBUTOS
    """

    #if(request.user.has_perm('crear_item')):----------------------------------------------------
    atributos= Atributo.objects.filter(ti_id=idTI)
    if request.method == 'POST':
        itemID = Item.objects.last()
        ti = TipoItem.objects.get(id_ti=idTI)

        contador=0

        for c in atributos:
            print(c.id_atributo)
            contador=contador+1
        ###alzar a dropbox-------validar file

        item=Item.objects.last()#SE OBTIENE EL ITEM CREADO RECIENTEMENTE
        list=[]
        for atributos in atributos:#SE RECORRE POR VALOR INGRESADO CONSULTANDO SI ES OBLIGARORIO Y ESTA VACIO-->MUESTRA ERROR
            ok = False
            if(atributos.tipo_dato == 'Boolean'):
                x = request.POST.getlist(atributos.tipo_dato)
                tiposAtributo = Atributo.objects.filter(ti_id=idTI, tipo_dato=atributos.tipo_dato)
                print(x)
                for ini in range(len(x)):
                    if(x[ini] == '' and tiposAtributo[ini].es_obligatorio == True):
                        ok=True
                        nombre=tiposAtributo[ini].nombre
                if(ok==True):
                    context = {
                        "mensaje": "EL ATRIBUTO ES OBLIGATRIO FAVOR INGRESE UN VALOR PARA EL ATRIBUTO: "+nombre,
                        "titulo": "NO INGRESO VALOR Y EL ATRIBUTO ES OBLIGATORIO",
                        "titulo_b1": "AÑADE VALOR",
                        "boton1": "/aggAtributos/" + str(idTI),
                        "titulo_b2": "NO HAY OPCION, AÑADE EL VALOR",
                        "boton2": "/aggAtributos/" + str(idTI),
                    }
                    return render(request, 'Error.html', context)
        list=["Decimal","Boolean","File","String","Date"]
        for ini in range(len(list)): #SI INGRESO VALORES CORRECTAMENTE LOS GUARDA RELACIONANDO CON EL ITEM CORRESPONDIENTE
            try:
                tiposAtributo = Atributo.objects.filter(ti_id=idTI, tipo_dato=list[ini])
                x=request.POST.getlist(list[ini])
            except:
                tiposAtributo=None

            if (tiposAtributo!=None):
                for valor in range(tiposAtributo.count()):
                    if(list[ini]=="File"):
                        list = []
                        for atr in tiposAtributo:
                            DOC = request.FILES.getlist(str(atr.id_atributo))
                            if (DOC != list):
                                print("no vacio",DOC[0])
                                ruta = str(ti.fase.id_Proyecto.id_proyecto) + "/" + str(itemID.id_item)
                                PATH = f'/{ruta}/{DOC[0]}'
                                SubirArchivo(DOC[0], PATH)
                                p = Atributo_Item(idAtributoTI=atr, id_item=item, valor=str(DOC[0]))
                                p.save()
                            else:
                                print("vacio",DOC)
                                p = Atributo_Item(idAtributoTI=atr, id_item=item, valor="Sin archivos adjuntos")
                                p.save()
                        break
                    else:
                        p = Atributo_Item(idAtributoTI=tiposAtributo[valor],id_item=item,valor=str(x[valor]))
                        p.save()

        itemID=Item.objects.last()
        ti=TipoItem.objects.get(id_ti=idTI)
        return redirect('gestion:relacionarItem',ti.fase.id_Proyecto.id_proyecto,itemID.id_item)

    contexto={
        'atributos':atributos,
        'true':True,
        'false':False,
    }
    return render (request,'items/aggAtributos.html',contexto)
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'Crear Item')

#RUBEN
def relacionarItem(request,id_proyecto,id_item):
    """
    SE MUESTRAN TODOS LOS ITEMS DE UN PROYECTO QUE SE ENCUENTRAN ACTIVOS EN EL MISMO, SE TENDRA LA POSIBILIDAD
    DE SELECCIONAR LOS MISMOS Y GUARDAR LAS RELACIONES CON EL ITEM ACTUAL, TAMBIEN SE CARGA LA TABLA VERSIONES CON
    EL ITEM ACTUAL Y LA VERSION 1 EN LA CREACION SE EVALUA:
    -QUE NO SE GENEREN CICLOS
    -QUE LA FASE 1 SEA OPCIONAL LAS RELACIONES
    -QUE SI NO ES LA PRIMERA FASE QUE TENGA RELACIONES DIRECTA O INDIRECTAMENTE CON LA FASE 1
    :param request:
    :param id_proyecto: ID DEL PROYECTO DEL CUAL QUITARA LOS ITEMS DE LAS FASES
    :param id_item: ID DEL ITEM CREANDO
    :return: REDIRIGE AL TEMPLATE RELACIONAR_ITEM
    """
    #if(request.user.has_perm('crear_item')):----------------------------------------------------

    proyecto=Proyecto.objects.get(id_proyecto=id_proyecto)#se obtiene el proyecto
    fases=Fase.objects.filter(id_Proyecto=proyecto)#se obtienen las fases del proyecto
    list = []#se guardaran todos los items del proyecto
    print(fases)
    itemActual=Item.objects.get(id_item=id_item)
    nroFase=0
    for fase in reversed(fases):
        print(fase)
        nroFase+=1
        if (itemActual.fase==fase):
            print("la fase en donde esta mi item es: ",fase)
            break
    mostrarActual=True
    mostrarSig=False
    mostrarAnte=False
    if(nroFase == 1):#si mi fase es la primera, solo le muestro items de la primera y segunda fase
        mostrarSig=True
    elif(nroFase == fases.count()):#si es la ultima, le muestro el anterior
        mostrarAnte=True
    else:#si no esta en la primera o ultima fase le muestro el ant y sig
        mostrarAnte=True
        mostrarSig=True
    if(mostrarActual==True):
        items = Item.objects.filter(actual=True,fase=itemActual.fase)
        print("se muestrar items de la fase actual: ",items)
        for i in range(items.count()):  ###todos los items del proyecto
            if items[i].fase.id_Proyecto.id_proyecto == id_proyecto and id_item != items[i].id_item:
                list.append(items[i].id_item)
                #print("se añadio en list item: ",items[i])
    if(mostrarSig==True):####### EVALUAR SI MOSTRAR SIG POR AHORA QUEDA
        faseSig=Fase.objects.get(id_Fase=(itemActual.fase.id_Fase+1))
        items = Item.objects.filter(actual=True,fase=faseSig)
        print("se muestrar items de la fase sig: ",items)
        for i in range(items.count()):  ###todos los items del proyecto
            if items[i].fase.id_Proyecto.id_proyecto == id_proyecto and id_item != items[i].id_item:
                list.append(items[i].id_item)
                #print("se añadio en list item: ",items[i])
    if(mostrarAnte==True):
        faseAnt=Fase.objects.get(id_Fase=(itemActual.fase.id_Fase-1))
        items = Item.objects.filter(actual=True,fase=faseAnt)
        print("se muestrar items de la fase ant: ",items)
        for i in range(items.count()):  ###todos los items del proyecto
            if items[i].fase.id_Proyecto.id_proyecto == id_proyecto and id_item != items[i].id_item:
                list.append(items[i].id_item)
                #print("se añadio en list item: ",items[i])
    print("lista a mostrar: ",list)
    items = Item.objects.filter(actual=True)
    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        some_var=request.POST.getlist('checkbox')
        #print(some_var)
        lis=[]
        proyecto = Proyecto.objects.get(id_proyecto=id_proyecto)
        fases = Fase.objects.filter(id_Proyecto=proyecto)
        item = Item.objects.filter(id_item=id_item)

        #VERIFICAR SI ES DE LA PRIMERA FASE SIN RELACIONES, SINO MOSTRAR ERROR
        if(lis==some_var):
            if fases[fases.count()-1].id_Fase!= item[0].fase.id_Fase:#sino es igual a la primera fase muestra error
                context = {
                    "mensaje": "EL ITEM NO ES DE LA PRIMERA FASE, POR ENDE DEBE DE CONTAR CON RELACION Y TENER DE FORMA DIRECTA O INDIRECTA RELACION CON LA PRIMERA FASE DEL PROYECTO ",
                    "titulo": "ITEM SIN RELACION",
                    "titulo_b1": "AÑADE RELACION",
                    "boton1": "/relacionarItem/" + str(id_proyecto)+"/"+str(id_item),
                    "titulo_b2": "CANCELAR ITEM",
                    "boton2": "/itemCancelado/",
                }
                return render(request, 'Error.html', context)

        if fases[fases.count()-1].id_Fase!= item[0].fase.id_Fase:#sino es igual a la primera fase muestra error
            #VERIFICAR SI TIENE RELACION CON LA F1
            if(primeraFase(id_proyecto, id_item, some_var)==True):
                context = {
                    "mensaje": "EL ITEM NO TIENE RELACION CON LA PRIMERA FASE POR ENDE NO ES VALIDO, FAVOR VOLVER A REALIZAR RELACIONES Y VOLVER CONSISTENTE EL ITEM ",
                    "titulo": "ITEM SIN RELACION CON LA FASE 1",
                    "titulo_b1": "VOLVER A AÑADIR RELACION",
                    "boton1": "/relacionarItem/" + str(id_proyecto)+"/" + str(id_item),
                    "titulo_b2": "CANCELAR ITEM",
                    "boton2": "/itemCancelado/",
                }
                return render(request, 'Error.html', context)

        #VERIFICAR SI SE GENERAN CICLOS--------- INCONSISTENCIAS

        registrarAuditoriaProyecto(request.user,'creo el item: '+str(item[0].nombre),id_proyecto,proyecto.nombre,item[0].fase.nombre)

        for id in some_var:###### SE GUARDAN LAS RELACIONES
            itemSeleccionado=Item.objects.get(id_item=id)
            if(itemSeleccionado.fase.id_Fase > itemActual.fase.id_Fase):#si el item es sucesor, sera apuntado por el item creado
                p = Relacion(fin_item=id,inicio_item=id_item)
                p.save()
                print(itemActual.nombre," --> ",itemSeleccionado.nombre)
            else:# sino es el sucesor, seguira siendo apuntado por los seleccionados
                p = Relacion(fin_item=id_item,inicio_item=id)
                p.save()
                print(itemActual.nombre," <-- ",itemSeleccionado.nombre)
        #----------------------------------------------------------#
        ## se puede volver generico si se restringe preguntando si el item es igual al ultimo
        version=Versiones(id_Version=1,id_item=id_item)#SE GUARDA LA VERSION
        version.save()
        #----------------------------------------------------------#

        return redirect('gestion:detallesFase',item[0].fase.id_Fase)
    else:
        return render(request, 'items/relacionarItem.html', {'form': items,'list':list,'itemActual':itemActual})
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'Crear Item')

def itemCancelado(request):
    """
    METODO PARA CANCELAR UN ITEM
    :return: REDIRIGE AL MENU PRINCIPAL
    """

    #if(request.user.has_perm('crear_item')):----------------------------------------------------

    x = Item.objects.last()
    x.delete()

    instanceItem = Atributo_Item.objects.filter(id_item = x)
    for i in instanceItem:
        i.delete()

    return  redirect("gestion:menu")
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'Crear Item')

def primeraFase(id_proyecto,id_item,some_var):
    """
    FUNCION QUE RECIBE UN IDPROYECTO, IDITEM Y LA LISTA DE ITEMS SELECCIONADOS EN LA SELECCION DE RELACIONES
    MEDIANTE TODOS LOS ITEMS DE LA PRIMERA FASE SE RECORREN DE A UNO Y SE MANDA  A LA FUNCION BUSQUEDA LA CUAL
    BUSCA EL IDITEM
    :param id_proyecto: ID DEL PROYECTO DEL CUAL SE DESEAN LOS ITEMS DE LA PRIMERA FASE
    :param id_item: ID DEL ITEM A BUSCAR
    :param some_var: LISTA DE RELACIONES SELECCIONADAS POR EL USUARIO
    :return: FALSO SI ENCUENTRA, TRUE SI NO
    """
    proyecto = Proyecto.objects.get(id_proyecto=id_proyecto)
    fases = Fase.objects.filter(id_Proyecto=proyecto)
    todosItems = Item.objects.filter(fase=fases[fases.count() - 1],actual=True)  # todos los items de la primera fase

    for item in todosItems:
        if(busqueda(item,id_item,some_var)==True):#id_item al cual llegar y some var sus nuevas relaciones
            return False
    return True


def busqueda(item,id_item,some_var):
    """
    SE BUSCA EL IDITEM MEDIANTE TODAS LAS RELACIONES DEL ITEM DE FORMA RECURSIVA,
    DEL ITEM SE OBTIENE SUS RELACIONES Y SE ITERA POR CADA UNO DE SUS RELACIONES Y A CADA UNO SE MANDA
    EN LA MISMA FUNCION, CUANDO SE ENCUENTRA EL ITEM RETORNA TRUE, CASO CONTRARIO FALSE
    :param item: ITEM EL CUAL SE RECORRERA SUS RELACIONES
    :param id_item: ID DEL ITEM EL CUAL SE BUSCA
    :param some_var: LISTA DE RELACIONES SELECCIONADAS POR EL USUARIO
    :return: TRUE SI ENCUENTRA, FALSE SI NO
    """
    try:
        relaciones = Relacion.objects.filter(inicio_item=item.id_item)
    except:
        relaciones = None

    for relaciones in relaciones:
        instanceItem= Item.objects.get(id_item=relaciones.fin_item)
        if(busqueda(instanceItem,id_item,some_var)==True):
            return True

    for id in some_var:
        if(str(id)==str(item.id_item)):######preguntar si es de otra fase si no se puede desde la misma porque --->apunta al contrario
            return True

    return False


### se usara mas tarde en la parte de relaciones
def ciclos(item,i,some_var):
    """FUNCION PARA ENCONTRAR CICLOS DE FORMA RECURSIVA"""
    try:
        relaciones = Relacion.objects.filter(inicio_item=i.id_item)
    except:
        relaciones = None

    if(relaciones != None):### si no tiene relaciones, compara
        for relaciones in relaciones:
            instanceItem= Item.objects.get(id_item=relaciones.fin_item)
            if(ciclos(item,instanceItem,some_var)==True):
                return True

    if(item.id_item==i.id_item):
        return True
    else:
        for x in some_var:
            if(str(x)==str(i.id_item)):
               return True

    return False


import dropbox
import tempfile


"""
dropbox
gestionitems.fpuna@gmail.com    
GestionItem20202
https://josevc93.github.io/python/Dropbox-y-python/
"""
def comite(request,pk):
    """
    LISTA LOS USUARIOS DEL COMITE DE UN PROYECTO EN ESPECIFICO
    :param request:
    :param pk: ID DEL PROYECTO DEL CUAL SE LISTARA LOS USUARIOS QUE SE ENCUENTRAN EN EL COMITE
    :return: REDIRIGE AL TEMPLATE COMITE
    """
    #if(request.user.has_perm('is_gerente')):----------------------------------------------------

    proyecto = User_Proyecto.objects.filter(proyecto_id=pk)
    gerente = User.objects.get(id=proyecto[0].user_id)
    print(gerente.username)

    comite = Comite.objects.all()
    form = Usuario.objects.all()
    proyectos=Proyecto.objects.get(id_proyecto=pk)
    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        #form.save()
        return redirect('gestion:comite',pk)
    else:
        list=[]
        if(comite != None):
            for i in range(form.count()):
                ok = False
                if form[i].esta_aprobado == True:
                    for x in comite:
                        if x.id_user == form[i].user.id and x.id_proyecto == pk:
                            ok=True
                if ok:
                   list.append(form[i].user.id)
        print(list)
        return render(request, 'proyectos/ver_comite.html', {'form': form,'list':list,'pk':pk,'proyectos':proyectos,'idGerente':gerente.id})
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'No es gerente')

#RUBEN
def AggComite(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    LISTA LOS USUARIOS DISPONIBLES PARA AGREGAR AL COMITE DE UN PROYECTO EN ESPECIFICO.
    :param pk: ID DEL PROYECTO AL CUAL SE AGREGARA EL COMITE
    :return: REDIRIGUE AL TEMPLATE AGGCOMITE
    """
    #if(request.user.has_perm('is_gerente')):----------------------------------------------------

    proyecto = User_Proyecto.objects.filter(proyecto_id=pk)
    gerente = User.objects.get(id=proyecto[0].user_id)
    print(gerente.username)

    proyectos=Proyecto.objects.get(id_proyecto=pk)
    comite= Comite.objects.all()
    form = Usuario.objects.all()
    registrados = User_Proyecto.objects.all()

    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        some_var=request.POST.getlist('checkbox')

        if ((len(some_var)+1)%2==0 or (len(some_var)+1)==1):# SE VALIDA QUE DEBE DE SER IMPAR Y MAYOR A 1
            context = {
                "mensaje": "EL NUMERO DE USUARIOS EN EL COMITE DEBE DE SER IMPAR Y MAYOR A UNO",
                "titulo": "ERROR AL SELECCIONAR",
                "titulo_b1": "AÑADIR COMITE",
                "boton1": "/AggComite/" + str(pk),
                "titulo_b2": "CANCELAR",
                "boton2": "/detallesProyecto/" + str(pk),
            }
            return render(request, 'Error.html', context)
        p=Comite(id_proyecto=pk,id_user=gerente.id)
        p.save()
        for id in some_var:###### SE GUARDAN EN USER_PROYECTOS LAS RELACIONES
            id_user =id
            p=Comite(id_proyecto=pk,id_user=id_user)
            p.save()

        return redirect('gestion:comite',pk)
    else:
        list=[]
        for i in range(form.count()):
            ok = False
            if form[i].esta_aprobado == True:
                for x in range(registrados.count()):
                    if registrados[x].proyecto_id == pk and  registrados[x].user_id == form[i].user.id and registrados[x].activo == True:# esta en el proyecto?
                        ok=True
                        for z in range(comite.count()):#si ya esta en el comite no
                            if form[i].user.id == comite[z].id_user and pk==comite[z].id_proyecto:
                                ok=False
            if ok:
               list.append(form[i].user.id)

        return render(request, 'proyectos/agg_comite.html', {'form': form,'list':list,'proyectos':proyectos,'idGerente':gerente.id})
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'No es gerente')

#RUBEN
def desvinculacionComite(request,pk,pk_user):
    """
    DESVINCULA UN USUARIO DE UN PROYECTO
    :param pk: ID DEL USUARIO
    :param pk_user: ID DEL USUARIO A DESVINCULAR
    """
    instanceUser = Comite.objects.filter(id_proyecto = pk, id_user = pk_user)
    instanceUser.delete()

def DeleteComite(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    LISTA LOS USUARIOS DEL COMITE Y DEJA SELECCIONAR USUARIOS PARA QUITAR DEL COMITE
    CUMPLIENDO LAS RESTRICCIONES DE QUE LA CANTIDAD DE USUARIOS SIGA SIENDO IMPAR Y MAYOR A UNO
    CASO CONTRARIO MUESTRA MENSAJE DE ERROR.
    :param pk: ID DEL PROYECTO DEL CUAL SE QUIERE DESHACER EL COMITE
    :return: RETORNA EN EL TEMPLATE COMITE
    """
    #if(request.user.has_perm('is_gerente')):----------------------------------------------------

    proyecto = User_Proyecto.objects.filter(proyecto_id=pk)
    gerente = User.objects.get(id=proyecto[0].user_id)
    print(gerente.username)

    comite = Comite.objects.all()
    form = Usuario.objects.all()
    proyectos=Proyecto.objects.get(id_proyecto=pk)

    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        some_var=request.POST.getlist('checkbox')

        if ((len(some_var)+1)%2==0 or (len(some_var)+1)==1):# SE VALIDA QUE DEBE DE SER IMPAR Y MAYOR A 1
            context = {
                "mensaje": "EL NUMERO DE USUARIOS EN EL COMITE DEBE DE SER IMPAR Y MAYOR A UNO",
                "titulo": "ERROR AL SELECCIONAR",
                "titulo_b1": "SELECCIONAR USUARIOS",
                "boton1": "/DeleteComite/" + str(pk),
                "titulo_b2": "CANCELAR",
                "boton2": "/detallesProyecto/" + str(pk),
            }
            return render(request, 'Error.html', context)

        for id in some_var:
            id_user =id
            desvinculacionComite(request,pk,id_user)


        return redirect('gestion:comite',pk)
    else:
        list=[]
        if(comite != None):
            for i in range(form.count()):
                ok = False
                if form[i].esta_aprobado == True:
                    for x in comite:
                        if x.id_user == form[i].user.id and x.id_proyecto == pk:
                            ok=True
                if ok:
                   list.append(form[i].user.id)
        print(list)
        return render(request, 'proyectos/delete_comite.html', {'form': form,'list':list,'pk':pk,'proyectos':proyectos,'idGerente':gerente.id})
    #else:------------------------------------SI NO TIENE EL PERMISO-------------------------------------
    #errorPermiso(request,'No es gerente')

def editar_ti(request,id_ti):
    tipo_item = get_object_or_404(TipoItem, id_ti=id_ti)
    Ti=TipoItem.objects.get(id_ti=id_ti)

    query_atributos = Atributo.objects.filter(ti_id=tipo_item.id_ti)
    AtributeFormSet = modelformset_factory(Atributo, form=AtributeForm,exclude=('id_atributo',), extra=0)
    if request.method=='POST':
        formset = AtributeFormSet(request.POST,request.FILES,queryset=query_atributos)
        formset_ti=TipoItemForm(request.POST,instance=tipo_item)
        print(formset_ti)
        if formset.is_valid() and formset_ti.is_valid() :
            print('es_valido')
            formset.save()
            instancia_ti=formset_ti.save(commit=False)
            instancia_ti.save()
            #user, accion, id_proyecto, proyecto, fase
            registrarAuditoriaProyecto(request.user,"Edito Tipo de Item '"+tipo_item.nombre+"'",tipo_item.fase.id_Proyecto.id_proyecto,tipo_item.fase.id_Proyecto.nombre,tipo_item.fase.nombre)
        else:
            print('no es valido')
            print(formset.errors)
            print(formset_ti.errors)
        return redirect('gestion:listar_tipo_item',tipo_item.fase.id_Proyecto.id_proyecto)
    else:
        print(tipo_item.fase.id_Proyecto)
        if validar_permiso(request.user,"is_gerente",tipo_item.fase.id_Proyecto) :  #primero se valida si es gerente en el proyecto actual
            if not Item.objects.filter(ti_id=id_ti).exists() : ##el item no tiene asociado ningun tipo de item
                formset_ti = TipoItemForm(instance=tipo_item)
                formset = AtributeFormSet(queryset=query_atributos)
                print('se imprime esto')
                context={
                    'formset':formset,
                    'formset_ti':formset_ti,
                    'tipo_item':tipo_item,
                    'proyectos':tipo_item.fase.id_Proyecto
                }
                return render(request,'proyectos/editar_tipo_item.html',context)
            else:
                context = {
                    "mensaje": "Este Tipo de item ya esta asociado a un item, por lo tanto no puede ser editado",
                    "titulo": "No se puede editar el tipo de item "+tipo_item.nombre,
                    "titulo_b2": "Volver Atras",
                    "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
                }
                return render(request, 'Error.html', context)
        else:
            context = {
                "mensaje": "No eres gerente de proyecto, por lo tanto no puede editar el tipo de item"+ tipo_item.nombre,
                "titulo": "No puede editar Tipo de item en este proyecto ",
                "titulo_b2": "Volver Atras",
                "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
            }
            return  render(request,"Error.html",context)


def agregar_atributo_ti(request, id_ti):
    form = formset_factory(AtributeForm, extra=1)
    tipo_item = TipoItem.objects.get(id_ti=id_ti)
    if(request.method=='POST'):
        my_form=form(request.POST)
        if my_form.is_valid():
            for form in my_form:
                n,o,t=recoge_datos_atributo(form)
                atributo1=Atributo.objects.create(nombre=n,es_obligatorio=o,tipo_dato=t,ti_id=id_ti)
                registrarAuditoriaProyecto(request.user, "agrego el atributo '"+atributo1.nombre +"' al tipo de item '" + tipo_item.nombre + "'",
                                           tipo_item.fase.id_Proyecto.id_proyecto, tipo_item.fase.id_Proyecto.nombre,
                                           tipo_item.fase.nombre)
        return  redirect('gestion:editar_ti',id_ti=id_ti)
    else:
        if validar_permiso(request.user, "is_gerente",tipo_item.fase.id_Proyecto):  # primero se valida si es gerente en el proyecto actual)
            if not Item.objects.filter(ti_id=id_ti).exists():
                contexto={
                    'formset':form,
                    'proyectos':tipo_item.fase.id_Proyecto
                }
                return render(request,'proyectos/crear_atributo.html',contexto)
            else:
                context = {
                    "mensaje": "Este Tipo de item ya esta asociado a un item, por lo tanto no se puede agregar un atributo mas",
                    "titulo": "No se puede agregar un atributo mas  al atributo del   tipo de item " + tipo_item.nombre,
                    "titulo_b2": "Volver Atras",
                    "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
                }
                return render(request, 'Error.html', context)
        else:
            context = {
                "mensaje": "No eres gerente de proyecto, por lo tanto no puedes agregar atributos  al tipo de item" + tipo_item.nombre,
                "titulo": "Conflicto de Permiso ",
                "titulo_b2": "Volver Atras",
                "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
            }
            return render(request, "Error.html", context)
def eliminar_atributo_ti(request,id_ti):
    tipo_item = get_object_or_404(TipoItem, id_ti=id_ti)
    if request.method=='POST':
        some_var = request.POST.getlist('checkbox')
        for id in some_var:
            instancia=Atributo.objects.get(id_atributo=id)
            registrarAuditoriaProyecto(request.user,
                                       "Elimino el atributo '" + instancia.nombre + "' del tipo de item '" + tipo_item.nombre + "'",
                                       tipo_item.fase.id_Proyecto.id_proyecto, tipo_item.fase.id_Proyecto.nombre,
                                       tipo_item.fase.nombre)
            instancia.delete()
        return redirect('gestion:editar_ti',id_ti=id_ti)
    if validar_permiso(request.user, "is_gerente",tipo_item.fase.id_Proyecto):  # primero se valida si es gerente en el proyecto actual)
        if not Item.objects.filter(ti_id=id_ti).exists():
            atributos=Atributo.objects.filter(ti_id=id_ti)
            contexto={
                'atributos':atributos,
                'tipo_item':tipo_item,
                'proyectos': tipo_item.fase.id_Proyecto
            }
            return  render(request,'proyectos/eliminar_atributo_ti.html',contexto)
        else:
            context = {
                "mensaje": "Este Tipo de item ya esta asociado a un item, por lo tanto no puede ser Eliminar un atributo de ello",
                "titulo": "No se puede Eliminar el atributo  tipo de item " + tipo_item.nombre,
                "titulo_b2": "Volver Atras",
                "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
            }
            return render(request, 'Error.html', context)
    else:
        context = {
            "mensaje": "No eres gerente de proyecto, por lo tanto no puedes eliminar atributos  del tipo de item" + tipo_item.nombre,
            "titulo": "Conflicto de Permiso ",
            "titulo_b2": "Volver Atras",
            "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
        }
        return render(request, "Error.html", context)

    atributos=Atributo.objects.filter(ti_id=id_ti)
    contexto={
        'atributos':atributos,
        'tipo_item':tipo_item,
    }
    return  render(request,'eliminar_atributo_ti.html',contexto)

def eliminar_tipo_item(request,id_ti):
   tipo_item=get_object_or_404(TipoItem, id_ti=id_ti)
   if validar_permiso(request.user,"is_gerente",tipo_item.fase.id_Proyecto):  #primero se valida si es gerente en el proyecto actual)
        if not Item.objects.filter(ti_id=id_ti).exists():
            Atributo.objects.filter(ti_id=id_ti).delete()
            fase=get_object_or_404(TipoItem, id_ti=id_ti).fase
            registrarAuditoriaProyecto(request.user,
                                       "Elimino el tipo de item '" + tipo_item.nombre + "'",
                                       tipo_item.fase.id_Proyecto.id_proyecto, tipo_item.fase.id_Proyecto.nombre,
                                       tipo_item.fase.nombre)
            tipo_item.delete()
            return redirect('gestion:listar_tipo_item',fase.id_Proyecto.id_proyecto)
        else:
            tipo_item=TipoItem.objects.get(id_ti=id_ti)
            context = {
                "mensaje": "Este Tipo de item ya esta asociado a un item, por lo tanto no puede ser Eliminado",
                "titulo": "No se puede Eliminar el tipo de item " + tipo_item.nombre,
                "titulo_b2": "Volver Atras",
                "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
            }
            return render(request, 'Error.html', context)
   else:
       context = {
           "mensaje": "No eres gerente de proyecto, por lo tanto no puede Eliminar el tipo de item" + tipo_item.nombre,
           "titulo": "No puede Eliminar el  Tipo de item en este proyecto ",
           "titulo_b2": "Volver Atras",
           "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
       }
       return render(request, "Error.html", context)


def DescargarArchivo(request,id_item,archivo):
    """
    FUNCION QUE DESCARGA UN ARCHIVO ADJUNTO DE UN ITEM SELECCIONADO, MEDIANTE EL TOKEN DE API DE DESARROLLADOR DE DROPBOX, VERIFICA SI EL ARCHIVO SELECCIONADO
    EXISTE, CASO CONTRARIO MUESTRA VENTANA DE ERROR, MEDIANTE EL NOMBRE DEL ARCHIVO SE GENERA LA DIRECCION DEL ARCHIVO EN DROPBOX QUE ES /ID_PROYECTO/ID_ITEM/NOMBRE-ARCHIVO
    MEDIANTE ELLO SE OBTIENE EL LINK DE DESCARGA DEL ARCHIVO Y SE ABRE LA URL MEDIANTE OPEN(URL) MOSTRANDO LA OPCION DE DESCARGA EN EL NAVEGADOR.
    :param id_item: ID DEL ITEM SELECCIONADO
    :param archivo: NOMBRE DEL ARCHIVO A DESCARGAR DEL ITEM
    :return: REDIRIGE A LA LISTA DE ATRIBUTOS DEL ITEM
    """
    item=Item.objects.get(id_item=id_item)
    dbx = dropbox.Dropbox(TOKEN)
    try:
        url = dbx.files_get_temporary_link('/'+str(item.fase.id_Proyecto.id_proyecto)+'/'+str(item.id_item)+'/'+archivo)
    except:
        url=None

    if(url==None):
        context = {
            "mensaje": "EL ATRIBUTO NO TIENE NINGUN ARCHIVO ADJUNTO",
            "titulo": "SIN ARCHIVO QUE DESCARGAR",
            "titulo_b1": "",
            "boton1": "",
            "titulo_b2": "LISTO",
            "boton2": "/detallesFase/" + str(item.fase.id_Fase),
        }
        return render(request, 'Error.html', context)

    webbrowser.open_new(url.link)
    return redirect('gestion:listar_atributos',item.ti.id_ti,item.id_item)

def SubirArchivo(DOC, PATH):
    """
    MEDIANTE EL TOKEN DE DESARROLLADOR DE DROPBOX SE REALIZA LA SUBIDA DEL ARCHIVO EN DROPBOX EN LA DIRECCION INDICADA ID_PROYECTO/ID_ITEM/NOMBRE-ARCHIVO.
    :param DOC: ARCHIVO SELECCIONADO POR EL USUARIO
    :param PATH: DIRECCION QUE TENDRA LA CARPETA EN DROPBOX
    """
    dbx = dropbox.Dropbox(TOKEN)
    dbx.files_upload(DOC.file.read(), PATH)

def validar_datos_form_atributo(form_set):
    for form in form_set:
        if form.cleaned_data=={}:
            return False
    return True


def validar_permiso(user,permiso, proyecto):
    if user.has_perm(permiso,proyecto):
        return True
    return False