from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from guardian.models import *
from django.contrib.auth.models import Permission,Group
from django.views.generic import TemplateView,ListView,UpdateView, CreateView
from django.urls import reverse_lazy
from .models import *
from .forms import FormProyecto,FormAyuda,SettingsUserFormJesus,PerfilUserEnEspera,RolForm
from time import gmtime, strftime
from .forms import FaseForm, FormProyectoEstados,FormItem
from django.db.models import Count
from django.utils.decorators import method_decorator
from .models import Proyecto,TipoItem,Atributo,Item,Fase,Atributo_Item,Relacion,Versiones,Comite, LineaBase, LB_item
from .forms import FormProyecto,TipoItemForm,AtributeForm,RolForm, LBForm, FormItemFase
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory
from django.forms.models import modelformset_factory
from guardian.shortcuts import assign_perm,get_groups_with_perms,remove_perm
from guardian.decorators import permission_required_or_403
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
import webbrowser
import dropbox
from django.contrib import messages

#### GLOBALES
DATA = []
LINK = []
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

from .funciones import *


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

    proyecto_validar=Proyecto.objects.get(id_proyecto=pk)

    if validar_permiso(request.user, "is_gerente",proyecto_validar)==False:  # primero se valida si es gerente en el proyecto actual)
        context = {
            "mensaje": "No eres gerente de proyecto, por lo tanto no puedes cambiar el estado" ,
            "titulo": "Conflicto de Permiso ",
            "titulo_b2": "Salir",
            "boton2": "/proyectos/",
        }
        return render(request, "Error.html", context)


    form=FormProyectoEstados(request.POST)
    p = Proyecto.objects.get(id_proyecto=pk)  ##### BUSCA EL PROYECTO CON ID
    if form.is_valid():
        x=form.cleaned_data
        z=x.get("estado")#### ESTADO SELECCIONADO
        #print(z)
        #print(pk)

        if(z=="FINALIZADO"):

            #registrarAuditoriaProyecto(request.user," cambio el estado a finalizado ",p.id_proyecto,p.nombre,"")
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
                    "mensaje": "CREE EL COMITE DE CAMBIO PARA CONTINUAR",
                    "titulo": "ERROR NO POSEE COMITE",
                    "titulo_b1": "CREAR COMITE",
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
                registrarAuditoriaProyecto(request.user, " cambio el estado a iniciado ", p.id_proyecto, p.nombre, "")
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
                registrarAuditoriaProyecto(request.user, " cambio el estado a cancelado ", p.id_proyecto, p.nombre, "")
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
        'proyecto':p,
        'proyectos': p
    }
    return render(request, 'Menu/estado_proyecto.html',context)





from threading import *


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

        ##correo se envia en segundo plano
        t = Timer(1,CorreoMail,args=(asunto,mensaje,"gerardocabrer@gmail.com"))
        t.start()

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

    return render(request,'Menu/contactos.html', context)


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
        proy=Proyecto.objects.get(id_proyecto=pk)
        for id in some_var:###### SE GUARDAN EN USER_PROYECTOS LAS RELACIONES
            id_user =id
            usuario=User.objects.get(id=id)
            registrarAuditoriaProyecto(request.user, " agrego al usuario "+str(usuario.username)+' al proyecto ', proy.id_proyecto, proy.nombre, "")
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
    '''
    Sirve para poder asignar o sacar los permisos es_gerente , es_administrador
        y cambiar el estado de un usario en especifico recibido como parametro,
        solo se permitira realizar esta accion al administrador de sistema, en caso de que el usuario
        no tenga dicho permiso se mostrara un mensaje de error

    :param request:
    :param pk:
    :return:
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
    '''
    Sirve para crear un tipo de item,en una fase en especifica, la fase especifica es recibida como
    parametro en la funcion, si los datos del tipo de item son validos(nombre y cantidad de atributos) , entonces
    la funcion redirige la continuidad de la accion a la view add_atribute, en caso de no ser valido
    muestra un mensaje (explicativo) de error
    :param request:
    :param id_fase:
    :return:
    '''
    ##validacion del estado del proyecto
    try:
        fase = Fase.objects.get(id_Fase=id_fase)
    except Fase.DoesNotExist:
        return HttpResponse('solicitud erronea, fase no existe', status=400)

    context = validar_proyecto_cancelado(fase.id_Proyecto.id_proyecto)
    if context != {}:

        return render(request, 'Error.html', context)

    if not validar_permiso(request.user, "is_gerente", fase.id_Proyecto):
        context = {
            "mensaje": "No eres gerente de proyecto, por lo tanto no puedes crear Tipo de Item",
            "titulo": "Conflicto de permiso ",
            "titulo_b2": "Salir",
            "boton2": "/proyectos/",
        }
        return render(request, "Error.html", context)

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
    '''
        Esta funcion realiza dos cosas , crea un tipo de item cuyo nombre sera el recibido como segundo parametro
        en la funcion , y un conjunto de atributos asociados al tipo de  item creado, la cantida de
        atributos creado es especificado como tercer parametro en la funcion, la funcion solo creara el tipo
        de item, si todos los atributos recibidos son validos, en caso contrario mostrara
        un mensaje de error al usuario.

    :param request:
    :param nombre_ti:
    :param cantidad_atributos:
    :param fase_id:
    :return:
    '''
    cantidad_atributos=int(cantidad_atributos)
    fase_id=int(fase_id)
    fase=Fase.objects.get(id_Fase=fase_id)
    #proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto_id)
    my_form = formset_factory(AtributeForm, extra=cantidad_atributos)
    if request.method == 'POST':
        my_form_set=my_form(request.POST)
        if(my_form_set.is_valid()):
            if validar_datos_form_atributo(my_form_set):
                tipo_item=TipoItem(nombre=nombre_ti,fase_id=fase_id)
                tipo_item.save()
                for form in my_form_set:
                    n,o,t=recoge_datos_atributo(form)
                    atributo1=Atributo.objects.create(nombre=n,es_obligatorio=o,tipo_dato=t,ti_id=tipo_item.id_ti)
                registrarAuditoriaProyecto(request.user, "Creo el tipo de item'" + tipo_item.nombre+ "'",
                                           fase.id_Proyecto.id_proyecto, fase.id_Proyecto.nombre,
                                           fase.nombre)
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
    '''
    Sirve para recoger los datos despues de un POST en un formulario de tipo de item, retorna el
        valor del nombre del tipo de item y la cantidad de atributos del tipo de item

    :param my_form:
    :return: String,Integer
    '''
    nombre = my_form.cleaned_data['nombre']
    valor = my_form.cleaned_data['cantidad']
    return nombre,valor

#jesus
def recoge_datos_atributo(form):
    '''
    Sirve para recoger los datos despues de un POST en un formulario de atributo, retorna el
            valor del nombre del atributo, si es obligatorio, y el tipo de dato

    :param form:
    :return: String, boolean,String
    '''
    nombre_atributo = form.cleaned_data.get('nombre')
    obligatoriedad = form.cleaned_data.get('es_obligatorio')
    tipo_dato_atibuto = form.cleaned_data.get('tipo_dato')
    return nombre_atributo,obligatoriedad,tipo_dato_atibuto

def recoger_datos_usuario_settings(form):
    '''
    Sirve para recoger los datos despues de un POST en un formulario de UsuarioSetting, retorna tres valores
        dos booleanos para determinar si es gerente y administrador y el estado del usuario

    :param form:
    :return: Boolean ,Boolean,String
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
    '''
    Funcion que permite agregar o sacar el permiso administrador de sistema a un usario recibido como parametro,
    si el segundo parametro es True entonces agrega el permiso a el usuario,
    en caso de que sea False lo saca
    :param user:
    :param is_admin:
    :return:
    '''
    content_type = ContentType.objects.get_for_model(Usuario)
    if (is_admin):  # se agrega el es_administrador
        permission = Permission.objects.get(content_type=content_type, codename='es_administrador')
        user.user_permissions.add(permission)
    else:  # se elimina el permiso es_administrador
        name_permission = 'es_administrador'
        permission = Permission.objects.get(content_type=content_type, codename=name_permission)
        user.user_permissions.remove(permission)

def add_permission_gerente(user,is_gerente):
    '''
    Funcion que permite agregar o sacar el permiso is_gerente a un usario recibido como parametro,
    si el segundo parametro es True entonces agrega el permiso gerente de proyecto  a el usuario,
    en caso de que sea False lo saca
    :param user:
    :param is_gerente:
    :return:
    '''
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
            add_permission_gerente(request.user,False)
            return redirect('gestion:menu')

    context = {
    'form': fase
    }
    return render(request, 'proyectos/crear_fase.html', context)




#RUBEN
def AggUser(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    MEDIANTE UN PROYECTO EXISTENTE, DA LA POSIBILIDAD DE AÑADIR MAS USUARIOS AL PROYECTO,
    FILTRANDO LOS USUARIOS QUE NO FORMAN PARTE DEL PROYECTO

    :param request:
    :param pk: ID DEL PROYECTO
    :return: AGGUSER.HTML
    """

    user= request.user## USER ACTUAL
    form = Usuario.objects.all()
    registrados = User_Proyecto.objects.all()

    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        #if form.is_valid():
        some_var=request.POST.getlist('checkbox')
        print(some_var)
        proyectos=Proyecto.objects.get(id_proyecto=pk)
        for id in some_var:
            id_user =id
            usuario = User.objects.get(id=id_user)
            registrarAuditoriaProyecto(request.user, "Añadio al proyecto al usuario: " + str(usuario.username),
                                       proyectos.id_proyecto, proyectos.nombre, "")

            p = User_Proyecto(user_id= id_user ,proyecto_id= pk,activo= True)
            p.save()

        #form.save()
        return redirect('gestion:detalles_Proyecto',pk)
    else:
        proyectos = Proyecto.objects.get(id_proyecto=pk)
        if validar_permiso(request.user, "is_gerente",proyectos) == False:  # primero se valida si es gerente en el proyecto actual)

            context = {
                "mensaje": "No eres gerente de proyecto, por lo tanto no añadir usuarios al proyecto",
                "titulo": "Conflicto de Permiso ",
                "titulo_b2": "Salir",
                "boton2": "/proyectos/",
            }
            return render(request, "Error.html", context)

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

#RUBEN
def UsersProyecto(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    LISTA LOS USUARIOS DE UN PROYECTO

    :param request:
    :param pk: ID DEL PROYECTO DEL CUAL SE LISTARAN LOS USUARIOS DEL MISMO
    :return: USERSPROYECTO.HTML
    """
    proyecto=Proyecto.objects.get(id_proyecto=pk)

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




@method_decorator(csrf_exempt)
def listar_relaciones(request,idItem):
    """
    LISTA LAS RELACIONES DE UN ITEM EN ESPECIFICO MEDIANTE EL ID DEL ITEM

    :param request:
    :param idItem: ID DEL ITEM DEL CUAL SE LISTARAN SUS RELACIONES
    :return: LISTAR_RELACIONES.HTML
    """
    relaciones= Relacion.objects.filter()

    item=Item.objects.all()
    itemActual=Item.objects.get(id_item=idItem)
    ### falta desvincular relacion o agregar nueva y cambiar version

    DATA = []
    LINK = []

    DATA.append({'key': itemActual.id_item, 'name': itemActual.nombre + ' cost:'+str(itemActual.costo), 'group': 'FASE'+str(itemActual.fase.id_Fase), 'color': "#2711E3"}, )
    fases = Fase.objects.filter(id_Proyecto=itemActual.fase.id_Proyecto, )
    num=0
    for i in fases:
        num +=1
        DATA.append({'key': 'FASE'+str(num), 'name': i.nombre , 'isGroup': 'true'}, )

    relaciones_trazabilidad(itemActual,DATA,LINK)
    izq=0
    band=0
    der=0
    for i in DATA:
        band += 1
        #print(i['name'])
        if str.isnumeric(str(i['key'])):
            it = Item.objects.get(id_item=i['key'])
            izq+=it.costo


    relaciones_trazabilidad_delante(itemActual,DATA,LINK)
    cont=0
    der=0
    for i in DATA:
        cont+=1
        if cont > band:
            it = Item.objects.get(id_item=i['key'])
            der+=it.costo
    der += itemActual.costo

    context={
        "relaciones":relaciones,
        "item":item,
        "itemActual":itemActual,
        'proyectos':itemActual.fase.id_Proyecto,
        'data':DATA,
        'link':LINK,
        'izq':izq,
        'der':der,
    }
    return render(request, 'items/trazabilidad.html', context)


def relaciones_trazabilidad(item,DATA,LINK):

    try:
        relaciones = Relacion.objects.filter(fin_item=item.id_item)
    except:
        relaciones = None

    for relaciones in relaciones:
        inicio = Item.objects.get(id_item=relaciones.inicio_item)
        ok = True
        for i in DATA:
            if i['key']== inicio.id_item:
                ok=False
        if ok:
            DATA.append({'key': inicio.id_item, 'name': inicio.nombre + ' cost:'+str(inicio.costo), 'group': 'FASE'+str(inicio.fase.id_Fase)}, )
            LINK.append({'from': inicio.id_item, 'to':item.id_item  }, )

        relaciones_trazabilidad(inicio, DATA,LINK)

def relaciones_trazabilidad_delante(item,DATA,LINK):

    try:
        relaciones = Relacion.objects.filter(inicio_item=item.id_item)
    except:
        relaciones = None

    for relaciones in relaciones:
        fin = Item.objects.get(id_item=relaciones.fin_item)
        ok = True
        for i in DATA:
            if i['key']== fin.id_item:
                ok=False
        if ok:
            DATA.append({'key': fin.id_item, 'name': fin.nombre + ' cost:'+str(fin.costo), 'group': 'FASE'+str(fin.fase.id_Fase)}, )
            LINK.append({'from': item.id_item, 'to':fin.id_item  }, )
        relaciones_trazabilidad_delante(fin, DATA,LINK)



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
    '''
    esta funcion permite importar tipos de item en un proyecto, para ello lista un conjunto
    de tipos de item , de los tipos de items
    disponibles para importar solo se muestran aquellos  aquellos tipos de items de otros proyectos en
    donde el usuario tambien este asociado, tambien filtra los tipos de items cuyo nombre ya no exista en el
    proyecto a donde se quiere importar
    La funcion solo permite importar tipos de items a  a los gerente de Proyecto  Si esta restriccion no se cumple
    se mostrara un mensaje (explicativo) del Error

    '''
    ##validacion del estado del proyecto
    try:
        fase = Fase.objects.get(id_Fase=id_fase)
    except Fase.DoesNotExist:
        return HttpResponse('solicitud erronea, fase no existe', status=400)

    context = validar_proyecto_cancelado(fase.id_Proyecto.id_proyecto)
    if context != {}:
        return render(request, 'Error.html', context)

    if not validar_permiso(request.user, "is_gerente", fase.id_Proyecto):
        context = {
            "mensaje": "No eres gerente de proyecto, por lo tanto no puedes crear Tipo de Item",
            "titulo": "Conflicto de permiso ",
            "titulo_b2": "Salir",
            "boton2": "/proyectos/",
        }
        return render(request, "Error.html", context)

    if(request.method=='POST'):
        print('es post')
        some_var = request.POST.getlist('checkbox')
        print(some_var)
        for id in some_var:
            print(id_fase)
            print(id)
            ti=TipoItem.objects.get(id_ti=id)#capturamos el tipo de item
            atributos=Atributo.objects.filter(ti_id=id) #optenemos todos los atributos de ese tipo de item
            ti.id_ti=None #clonamos el tipo de item
            ti.fase_id=id_fase
            ti.save() #guardamos
            for atributo in atributos: #iteramos cada atributo clonarlos y relacionar con el tipo de item nuevo
                    atributo.id_atributo=None
                    atributo.ti_id=ti.id_ti
                    atributo.save()
            registrarAuditoriaProyecto(request.user, "Importo el tipo de item: "+ti.nombre,
                                       fase.id_Proyecto.id_proyecto, fase.id_Proyecto.nombre,
                                       fase.nombre)
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
    '''
    Esta funcion permite obtener todos los tipos de item de un proyecto especifico recibido como parametro,
    en caso de que el proyecto no tenga ningun tipo de items, la funcion  retorna una lista vacia
    :param id_proyecto:
    :return: Lista de Tipo de Items
    '''
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
    #success_url = reverse_lazy("gestion:menu",)
    """-succes_url: es especifica a que direccion se redirigira la view una vez actualizado el objeto dentro del modelo"""
    def post(self, request, *args, **kwargs):
        """    La funcion redeclara es la de post, en donde se realiza una modificacion del nombre declarado
            para la creacion, agregandole el id del proyecto perteneciente delate, esto para el reconocimiento
            del proyecto pertenciente de este Rol a crear"""
        request.POST = request.POST.copy()
        request.POST['name']= self.kwargs['proyecto']+'_'+request.POST['name']
        return super(CrearRol,self).post(request,**kwargs)

    def get_success_url(self):
        return reverse_lazy('gestion:asignar_rol_proyecto',kwargs={'nombre': self.object.name})

def validar_usuario(user):
    '''
    Valida al usuario al inicio del sistema, si el usuario recibido como parametro es el primer usuario
    del sistema se le asigna el rol de administrador  del sistema y se le agrega el estado aprobado, para
    los otros usuarios nuevos (que se logearon por primera vez)  por default se le asigna el esta
    Desaprobado, para que luego el administrador del Sistema lo apruebe
    :param user:
    :return:
    '''
    if (User.objects.count() == 2):
        add_permission_admin(user, True)
        usuario = Usuario.objects.filter(user_id=user.id).exists()
        if not usuario:
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
    def get_success_url(self):
        return reverse_lazy('gestion:modificar_rol_proyecto',kwargs={'nombre': self.object.name})

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

from django.http import HttpResponse



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
    try:
        fase = Fase.objects.get(id_Fase=Faseid)
    except:
        return HttpResponse(request,"id de fase invalida",status=400)

    proyecto=Proyecto.objects.get(id_proyecto=fase.id_Proyecto.id_proyecto)
    fases=Fase.objects.filter(id_Proyecto=proyecto)

    if validar_permiso(request.user,"is_gerente",fase.id_Proyecto) or request.user.has_perm('crear_item',proyecto) and validar_rol_fase('crear_item',fase,request.user):
        print('tiene el permiso de crear_item')
    else:
        messages.error(request,"NO SE POSEE EL PERMISO: crear_item" + " SOLICITE EL PERMISO CORRESPONDINTE PARA REALIZAR LA ACCION")
        return redirect('gestion:detallesFase',fase.id_Proyecto.id_proyecto)

    #if(proyecto.estado != "INICIADO"):
    #    messages.error(request,"EL PROYECTO NO SE ENCUENTRA INICIADO POR ENDE NO SE PUEDE CREAR ITEMS AUN, FAVOR CAMBIE SU ESTADO A INICIADO SI DESEA REALIZAR ESTA ACCION, ESTADO ACTUAL DEL PROYECTO: "+str(proyecto.estado))
    #    return redirect('gestion:detallesFase',fase.id_Proyecto.id_proyecto)

    if(fase1SinItems(fases,fase)==True):# si no es de la primera fase y la F1 no tiene items muestra error
        messages.error(request,"LA FASE ANTERIOR NO CONTIENE ITEMS POR ENDE NO PODRA RELACIONAR CON LA PRIMERA FASE, CREE ITEM EN LA FASE ANTERIOR A ESTA Y LUEGO INTENTE NUEVAMENTE")
        return redirect('gestion:detallesFase',fase.id_Proyecto.id_proyecto)

    if (hayTiFase(fase)):  # muestra mensaje de error si no hay TI no se puede crear item
        messages.error(request,"LA FASE NO CONTIENE NINGUN TI Y  UN ITEM NECESARIAMENTE REQUIERE UNA, ASI QUE CREELA E INTENTE NUEVAMENTE")
        return redirect('gestion:detallesFase',fase.id_Proyecto.id_proyecto)

    form= FormItem(request.POST)
    if form.is_valid():
        form.save(commit=False)

        datosFormulario= form.cleaned_data
        fase= Fase.objects.get(id_Fase=Faseid)
        item=Item(nombre=datosFormulario.get('nombre'),descripcion=datosFormulario.get('descripcion'),costo=datosFormulario.get('costo'),fase=fase)
        item.save()
        return redirect('gestion:agg_listar_tipo_item',Faseid)
    contexto={
        "form":form
    }
    return render (request,'items/Item.html',contexto)

#RUBEN
def agg_listar_tipo_item(request,id_fase):
    """
    LISTA LOS TIPOS DE ITEMS DE UNA FASE EN ESPECIFICA, RECIBE EL ID DE LA FASE, AL SELECCIONAR EL TI SE GUARDA EN EL ITEM
    CORRESPONDIENTE Y SE REDIRIGE A UNA VENTANA EN LA QUE SE CARGAN LOS ATRIBUTOS DE DICHO TI SELECCIONADO
    :param request:
    :param Fase: ID DE LA FASE DEL CUAL DEBE LISTAR LOS TI
    :return: AGGTI.HTML
    """

    fase_proyecto=Fase.objects.get(id_Fase=id_fase)
    proyecto=Proyecto.objects.get(id_proyecto=fase_proyecto.id_Proyecto.id_proyecto)

    if validar_permiso(request.user,"is_gerente",fase_proyecto.id_Proyecto) or request.user.has_perm('crear_item',proyecto) and validar_rol_fase('crear_item',fase_proyecto,request.user):
        print('tiene el permiso de crear_item')
    else:
        messages.error(request,"NO SE POSEE EL PERMISO: crear_item" + " SOLICITE EL PERMISO CORRESPONDINTE PARA REALIZAR LA ACCION")
        return redirect('gestion:detallesFase',fase_proyecto.id_Proyecto.id_proyecto)

    item_id=Item.objects.last()
    tipoItem = TipoItem.objects.filter(fase_id=id_fase)
    if(tipoItem.count() == 0):
        return HttpResponse(request,"id de fase invalida",status=400)

    if request.method == 'POST':
        x=request.POST.get('ti')
        item=Item.objects.last()
        tipoItem2 = TipoItem.objects.filter(nombre=x,fase_id=id_fase)
        print(tipoItem2)
        item.ti =tipoItem2[0]
        item.save()

        return redirect('gestion:aggAtributos',tipoItem2[0].id_ti)

    contexto={
        'TipoItem':tipoItem,
        'id_item':item_id.id_item
    }
    return render (request,'items/aggTI.html',contexto)

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
    atributos= Atributo.objects.filter(ti_id=idTI)

    if validar_permiso(request.user,"is_gerente",atributos[0].ti.fase.id_Proyecto) or request.user.has_perm('crear_item',atributos[0].ti.fase.id_Proyecto) and validar_rol_fase('crear_item',atributos[0].ti.fase,request.user):
        print('tiene el permiso de crear_item')
    else:
        messages.error(request,"NO SE POSEE EL PERMISO: crear_item" + " SOLICITE EL PERMISO CORRESPONDINTE PARA REALIZAR LA ACCION")
        return redirect('gestion:detallesFase',atributos.ti.fase.id_Proyecto.id_proyecto)

    if(atributos.count() == 0):
        return HttpResponse(request,"id de TI invalida",status=400)

    if request.method == 'POST':
        itemID = Item.objects.last()
        ti = TipoItem.objects.get(id_ti=idTI)
        contador=0

        for c in atributos:
            print(c.id_atributo)
            contador=contador+1

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
                if( ok == True ):
                    messages.error(request, "EL ATRIBUTO ES OBLIGATRIO FAVOR INGRESE UN VALOR PARA EL ATRIBUTO: "+nombre)
                    return redirect('gestion:aggAtributos', idTI)

        list=["Decimal","Boolean","File","String","Date"]
        for ini in range(len(list)): #SI INGRESO VALORES CORRECTAMENTE LOS GUARDA RELACIONANDO CON EL ITEM CORRESPONDIENTE
            print('este es el valor de ini'+str(ini))
            print(list[ini])
            try:
                tiposAtributo = Atributo.objects.filter(ti_id=idTI, tipo_dato=list[ini])
                x=request.POST.getlist(list[ini])
            except:
                tiposAtributo=None

            if (tiposAtributo!=None):
                for valor in range(tiposAtributo.count()):
                    if(list[ini]=="File"):
                        list2 = []
                        for atr in tiposAtributo:
                            DOC = request.FILES.getlist(str(atr.id_atributo))
                            if (DOC != list2):
                                print("no vacio",DOC[0])
                                ruta = str(ti.fase.id_Proyecto.id_proyecto) + "/" + str(itemID.id_item)
                                PATH = f'/{ruta}/{DOC[0]}'
                                #SubirArchivo(DOC[0], PATH)
                                #print("--",DOC[0])

                                ##se sube archivo a dropbox en segundo plano
                                t2 = Thread(
                                    target=SubirArchivo,
                                    args=(DOC[0],PATH),
                                )
                                t2.start()

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
    item_id = Item.objects.last()
    contexto={
        'atributos':atributos,
        'true':True,
        'false':False,
        'id_item':item_id.id_item
    }
    return render (request,'items/aggAtributos.html',contexto)

def lista_items_relacion(itemActual, fases,id_proyecto,id_item):


    list = []
    nroFase = 0
    ok=False
    for fase in reversed(fases):
        print(fase)
        nroFase += 1
        if (itemActual.fase == fase):
            print("la fase en donde esta mi item es: ", fase," nro ",nroFase)
            ok=True
            break

    if(ok==False):

        return HttpResponse("id de TI invalida",status=400)

    mostrarActual = True
    mostrarSig = False# ya no muestra la sig fase
    mostrarAnte = False

    if(fases.count() != 1):
        if(nroFase == 1):
            print("")
        else:
            mostrarAnte = True

    if (mostrarActual == True):
        items = Item.objects.filter(actual=True, fase=itemActual.fase)
        print("se muestrar items de la fase actual: ", items)
        for i in range(items.count()):  ###todos los items del proyecto
            if items[i].fase.id_Proyecto.id_proyecto == id_proyecto and id_item != items[i].id_item:
                list.append(items[i].id_item)
                # print("se añadio en list item: ",items[i])
    if (mostrarSig == True):  ####### EVALUAR SI MOSTRAR SIG POR AHORA QUEDA
        faseSig = Fase.objects.get(id_Fase=(itemActual.fase.id_Fase + 1))
        items = Item.objects.filter(actual=True, fase=faseSig)
        print("se muestrar items de la fase sig: ", items)
        for i in range(items.count()):  ###todos los items del proyecto
            if items[i].fase.id_Proyecto.id_proyecto == id_proyecto and id_item != items[i].id_item:
                list.append(items[i].id_item)
                # print("se añadio en list item: ",items[i])
    if (mostrarAnte == True):
        faseAnt = Fase.objects.get(id_Fase=(itemActual.fase.id_Fase - 1))
        items = Item.objects.filter(actual=True, fase=faseAnt)
        print("se muestrar items de la fase ant: ", items)
        for i in range(items.count()):  ###todos los items del proyecto
            if items[i].fase.id_Proyecto.id_proyecto == id_proyecto and id_item != items[i].id_item:
                list.append(items[i].id_item)
                # print("se añadio en list item: ",items[i])
    print("lista a mostrar: ", list)

    return list

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
    try:
        proyecto=Proyecto.objects.get(id_proyecto=id_proyecto)#se obtiene el proyecto
        fases=Fase.objects.filter(id_Proyecto=proyecto)#se obtienen las fases del proyecto
        itemActual=Item.objects.get(id_item=id_item)
        list=[]
        list=lista_items_relacion(itemActual,fases,id_proyecto,id_item)
        items = Item.objects.filter(actual=True)
    except:

        return HttpResponse(request, "id de TI invalida",status=400)


    if validar_permiso(request.user,"is_gerente",proyecto) or request.user.has_perm('crear_item',proyecto) and validar_rol_fase('crear_item',itemActual.fase,request.user):
        print('tiene el permiso de crear_item')
    else:
        context = {
            "mensaje": "NO SE POSEE EL PERMISO: crear_item" + " SOLICITE EL PERMISO CORRESPONDINTE PARA REALIZAR LA ACCION",
            "titulo": "SIN PERMISO",
            "titulo_b1": "",
            "boton1": "",
            "titulo_b2": "SALIR",
            "boton2": "/proyectos/",
        }
        return render(request, 'Error.html', context)


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


def comite(request,pk):
    """
    LISTA LOS USUARIOS DEL COMITE DE UN PROYECTO EN ESPECIFICO
    :param request:
    :param pk: ID DEL PROYECTO DEL CUAL SE LISTARA LOS USUARIOS QUE SE ENCUENTRAN EN EL COMITE
    :return: REDIRIGE AL TEMPLATE COMITE
    """

    proyecto = User_Proyecto.objects.filter(proyecto_id=pk)
    gerente = User.objects.get(id=proyecto[0].user_id)

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

#RUBEN
def AggComite(request,pk):#esta enlazado con la clase FaseForm del archivo getion/forms
    """
    LISTA LOS USUARIOS DISPONIBLES PARA AGREGAR AL COMITE DE UN PROYECTO EN ESPECIFICO.
    :param pk: ID DEL PROYECTO AL CUAL SE AGREGARA EL COMITE
    :return: REDIRIGUE AL TEMPLATE AGGCOMITE
    """
   ##ESte es lo que yo(presi) le agregue
    try:
        proyectos = Proyecto.objects.get(id_proyecto=pk)
    except Proyecto.DoesNotExist:
        return HttpResponse("Proyecto no existe",status=400)

    try:
        proyecto = User_Proyecto.objects.filter(proyecto_id=pk)
    except:
        return HttpResponse("Proyecto no existe",status=400)

    gerente = User.objects.get(id=proyecto[0].user_id)
    print(gerente.username)

    proyecto_validar=Proyecto.objects.get(id_proyecto=pk)

    if validar_permiso(request.user, "is_gerente",proyecto_validar)==False:  # primero se valida si es gerente en el proyecto actual)
        messages.error(request, 'No eres gerente de proyecto, por lo tanto no puedes crear el comite de cambio')
        return redirect('gestion:comite', pk)

    proyectos=Proyecto.objects.get(id_proyecto=pk)
    comite= Comite.objects.all()
    form = Usuario.objects.all()
    registrados = User_Proyecto.objects.all()

    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        some_var=request.POST.getlist('checkbox')

        if ((len(some_var)+1)%2==0 or (len(some_var)+1)==1):# SE VALIDA QUE DEBE DE SER IMPAR Y MAYOR A 1
            messages.error(request,'EL NUMERO DE USUARIOS EN EL COMITE DEBE DE SER IMPAR Y MAYOR A UNO')
            return redirect('gestion:AggComite',pk)
        p=Comite(id_proyecto=pk,id_user=gerente.id)
        p.save()
        for id in some_var:###### SE GUARDAN EN USER_PROYECTOS LAS RELACIONES
            id_user =id
            usuario=User.objects.get(id=id_user)
            registrarAuditoriaProyecto(request.user,"Añadio al comite de cambio al usuario: "+str(usuario.username),proyectos.id_proyecto,proyectos.nombre,"")
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

    proyecto = User_Proyecto.objects.filter(proyecto_id=pk)
    gerente = User.objects.get(id=proyecto[0].user_id)
    print(gerente.username)

    proyecto_validar=Proyecto.objects.get(id_proyecto=pk)

    if validar_permiso(request.user, "is_gerente",proyecto_validar)==False:  # primero se valida si es gerente en el proyecto actual)
        messages.error(request, 'No eres gerente de proyecto, por lo tanto no puedes eliminar el comite de cambio')
        return redirect('gestion:comite', pk)

    comite = Comite.objects.all()
    form = Usuario.objects.all()
    proyectos=Proyecto.objects.get(id_proyecto=pk)

    if request.method == 'POST': #preguntamos primero si la petición Http es POST ||| revienta todo con este
        some_var=request.POST.getlist('checkbox')

        if ((len(some_var)+1)%2==0 or (len(some_var)+1)==1):# SE VALIDA QUE DEBE DE SER IMPAR Y MAYOR A 1
            messages.error(request,'EL NUMERO DE USUARIOS EN EL COMITE DEBE DE SER IMPAR Y MAYOR A UNO')
            return redirect('gestion:DeleteComite',pk)

        for id in some_var:
            id_user =id
            usuario = User.objects.get(id=id_user)
            registrarAuditoriaProyecto(request.user, "Desvinculo del comite de cambio al usuario: " + str(usuario.username),
                                       proyectos.id_proyecto, proyectos.nombre, "")

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

def editar_ti(request,id_ti):
    '''
       Esta funcion permite editar el nombre del Tipo de Item y los atributos del mismo, para ello lista
       todos los atributos del Tipo de Item y para cada atributo da la posibilidad de editar sus caracteristicas
       (nombre,Tipo Dato, Obligatoriedad), tambien da la opcion de agregar nuevos atributos y eliminar atributos ya
       existentes del Tipo de Item.
       La funcion solo permite editar Tipo de items a los gerente de Proyecto, y tambien valida que solo se podran
       editar aquellos tipo de item que no esten asociados aun a un Item. Si estas ultimas dos restricciones no se
       cumplen se mostrara un mensaje (explicativo) del Error

    :param request:
    :param id_ti:
    :return: None
    '''
    try:
        tipo_item = TipoItem.objects.get(id_ti=id_ti)
        print('editar_tipo_item')
    except TipoItem.DoesNotExist:
        return HttpResponse('solicitud erronea, tipo de item no existe', status=400)

    context=validar_proyecto_cancelado(tipo_item.fase.id_Proyecto.id_proyecto)
    if context!={}:
        return render(request, 'Error.html', context)

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
    '''
    Esta funcion permite agregar un nuevo atributo a un Tipo de Item pasado como parametro, para el nuevo
    atributo se deberan de completar sus caracteristicas(nombre,tipo de dato,obligatoriedad), si no se
    definen todas las carateristicas del atributo, se mostrar un mensaje de error , y le dara la posibilidad
    de  intentarlo de nuevo.
    La funcion solo permite agregar un atributo al  Tipo de item a los gerente de Proyecto, y tambien valida
    que solo se podran agregar atributos  aquellos tipo de item que no esten asociados aun a un Item. Si estas ultimas dos restricciones no se
    cumplen se mostrara un mensaje (explicativo) del Error

    :param request:
    :param id_ti:
    :return:
    '''
    form = formset_factory(AtributeForm, extra=1)

    try:
        tipo_item = TipoItem.objects.get(id_ti=id_ti)
        print('agregar_atriburo_tipo_item')
    except TipoItem.DoesNotExist:
        return HttpResponse('solicitud erronea, tipo de item no existe', status=400)

    context = validar_proyecto_cancelado(tipo_item.fase.id_Proyecto.id_proyecto)
    if context != {}:
        return render(request, 'Error.html', context)

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
    '''
    Esta funcion lista todos los atributos (con una opcion de seleccionar )de un Tipo de Item
    pasado como parametro, para cada atributo seleccionado por el usuario , se eliminara el atributo del
    tipo item
    La funcion solo permite eliminar atributos de Tipo de items a los gerente de Proyecto, y tambien valida
    que solo se podran eliminar aquellos  atributos de tipo de item que no esten asociados aun a un Item. Si estas ultimas dos restricciones no se
    cumplen se mostrara un mensaje (explicativo) del Error

    :param request:
    :param id_ti:
    :return:
    '''
    try:
        tipo_item = TipoItem.objects.get(id_ti=id_ti)
    except TipoItem.DoesNotExist:
        return HttpResponse('solicitud erronea, tipo de item no existe', status=400)

    ##validacion del estado del proyecto
    context = validar_proyecto_cancelado(tipo_item.fase.id_Proyecto.id_proyecto)
    if context != {}:
        return render(request, 'Error.html', context)

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
       # print('es gerente')
        if not Item.objects.filter(ti_id=id_ti).exists():
            atributos=Atributo.objects.filter(ti_id=id_ti)
            contexto={
                'atributos':atributos,
                'tipo_item':tipo_item,
                'proyectos': tipo_item.fase.id_Proyecto
            }
            return render(request,'proyectos/eliminar_atributo_ti.html',contexto)
        else:
            context = {
                "mensaje": "Este Tipo de item ya esta asociado a un item, por lo tanto no puede ser Eliminar un atributo de ello",
                "titulo": "No se puede Eliminar el atributo  tipo de item " + tipo_item.nombre,
                "titulo_b2": "Volver Atras",
                "boton2": "/lista/tipo/item/" + str(tipo_item.fase.id_Proyecto.id_proyecto),
            }
            return render(request, 'Error.html', context)
    else:
        #print('No es gerente')
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

from django.http import HttpResponse

def eliminar_tipo_item(request,id_ti):
   '''
    Esta funcion permite eliminar un Tipo de Item pasado como parametro, como consecuencia esta funcion tambien
    elimina todos los atributos relacionados a ese Tipo de Item.
    La funcion solo permite eliminar el tipo de Item  a los gerente de Proyecto, y tambien valida
    que solo se podran eliminar aquellos  tipo de item que no esten asociados aun a un Item. Si estas
    ultimas dos restricciones no se cumplen se mostrara un mensaje (explicativo) del Error

   :param request:
   :param id_ti:
   :return:
   '''
   print(id_ti)
   try:
       tipo_item = TipoItem.objects.get(id_ti=id_ti)
   except TipoItem.DoesNotExist:
        return HttpResponse('solicitud erronea, tipo de item no existe', status=400)

    ##validacion del estado del proyecto
   context = validar_proyecto_cancelado(tipo_item.fase.id_Proyecto.id_proyecto)
   if context != {}:
       return render(request, 'Error.html', context)

   if validar_permiso(request.user,"is_gerente",tipo_item.fase.id_Proyecto):  #primero se valida si es gerente en el proyecto actual)
        print(' es gerente')
        print('ACA IMPRIMO ALGOOO',Item.validar_ti_item(id_ti))
        if not Item.validar_ti_item(id_ti):
            print('acaaa')
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
       print('no es gerente')
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
    print("SUBIO A DROPBOX ---> ", DOC)



def validar_datos_form_atributo(form_set):
    '''
    Esta funcion permite validar una coleccion de forms del Modelo Atributo recibidos desde un POST, La validacion consiste en
    verificar que ninguno de los form recibidos es un diccionario vacio (es decir el usuario no ingreso
    nada) y con eso validar la consistencia del sistema, en caso de que el usuario de olvido de ingresar algun
    dato de algun Atributo, la funcion retornara False, si, no todos los forms recibidos son correctos entonces
    se retornara True
    :param form_set:
    :return: Boolean
    '''
    for form in form_set:
        if form.cleaned_data=={}:
            return False
    return True

def Asignar_Rol_usuario_proyecto(request,id_Fase,id_usuario):
    '''
    Esta funcion es la encargada de asignar un conjunto de roles a un usuario en una determinada fase,
    ese conjunto de roles se optiene de un POST, de los roles recibidos se verifica cada uno para determinar
    si el usuario ya lo tiene, si es asi no hace nada, pero en caso que el usuario no lo tenga, entoces
    se registra ese rol  a el usuario en esa fase.
    De los roles que no se marco se lo  llama a la funcion eliminar_rol_proyecto_usuario para que tambien
    elimine aquellos roles que el gerente no marco
    :param request:
    :param id_Fase:
    :param id_usuario:
    :return:
    '''
    try:
        fase = Fase.objects.get(id_Fase=id_Fase)
    except Fase.DoesNotExist:
        return HttpResponse('solicitud erronea, fase no existe', status=400)

    try:
        usuario = User.objects.get(id=id_usuario)
    except User.DoesNotExist:
        return HttpResponse('solicitud erronea, usuario no existe', status=400)

    proyecto=fase.id_Proyecto

    context = validar_proyecto_cancelado(proyecto.id_proyecto)
    if context != {}:
        messages.error(request, 'No se puede trabajar , el proyecto ya esta cancelado')
        return redirect('gestion:detalles_Proyecto', fase.id_Proyecto.id_proyecto)

    if  obtener_todos_roles_proyecto(proyecto.id_proyecto)==[] :
        messages.error(request,'El Proyecto aun no tiene roles, creelos antes de asingar')
        return redirect('gestion:detallesProyecto',fase.id_Proyecto.id_proyecto)

    if  request.method=='POST':
        rolNombreProyecto=[]
        rolesProyecto = Group.objects.all() #Otengo Todo los roles del Proyecto
        for rolProyecto in rolesProyecto:
            id_proyecto, nombre_rol = rolProyecto.name.split('_')
            if int(id_proyecto) == proyecto.id_proyecto :
                rolNombreProyecto = rolNombreProyecto+[rolProyecto.name] #Todo los roles le agrego a una lista

        roles = request.POST.getlist('roles') #Obtengo los roles del Form
        print('roles del form',roles)
        for rol in roles:
            group=Group.objects.get(name=rol)
            rolNombreProyecto.remove(rol)
            if not FASE_ROL.objects.filter(id_fase_id=fase.id_Fase,id_rol_id=group.id,id_usuario_id=usuario.id).exists():
                FASE_ROL.objects.create(id_fase_id=id_Fase,id_rol=group,id_usuario=usuario)
                id_proyecto, nombre_rol = group.name.split('_')
                registrarAuditoriaProyecto(request.user, "Asigno  el rol: "+ nombre_rol  +" al usuario '" + usuario.username + "'",
                                           fase.id_Proyecto.id_proyecto, fase.id_Proyecto.nombre,
                                           fase.nombre)
            usuario.groups.add(group)
        if rolNombreProyecto:
            print('roles a eliminar',rolNombreProyecto)
            eliminar_rol_proyecto_usuario(fase.id_Fase,rolNombreProyecto,usuario,request.user)


        return redirect('gestion:seleccionar_usuario_rol',id_fase=id_Fase)
    else:
        if validar_permiso(request.user, "is_gerente", fase.id_Proyecto):  # primero se valida si es gerente en el proyecto actual
            roles=Group.objects.all()
            roles_listar=[]
            roles_listar2 = []
            fase=Fase.objects.get(id_Fase=id_Fase)
            for rol in roles:
                id_proyecto,nombre_rol=rol.name.split('_')
                if(int(id_proyecto)==fase.id_Proyecto.id_proyecto):
                    if FASE_ROL.objects.filter(id_fase_id=fase.id_Fase,id_rol_id=rol.id,id_usuario_id=usuario.id).exists():
                        ban=1
                    else:
                        ban=0
                    roles_listar=roles_listar+[
                        {
                            'nombre_lindo': nombre_rol,
                            'nombre_real': rol.name,
                            'ban':ban
                        }
                    ]
            contexto={
                'roles':roles_listar,
                'proyectos':proyecto
            }
            return  render(request,'proyectos/asignarRol.html',contexto)
        else:
            messages.error(request, 'No es gerente de proyecto, no puede asignar roles')
            return redirect('gestion:detalles_Proyecto', fase.id_Proyecto.id_proyecto)

def asignar_rol_proyecto(request,nombre):
    '''Esta funcion es la encargada se asignar todos los permisos de un rol, pero para un determinado
    proyecto utilizando django guardia, para ello obtiene todos los permisos del rol y asigna ese permiso
    a al mismo rol pero para un determinado proyecto.
    '''
    id_proyecto,nombre_rol=nombre.split('_')
    proyecto=Proyecto.objects.get(id_proyecto=id_proyecto)
    rol=Group.objects.get(name=nombre)
    permisos=rol.permissions.all()
    for permiso in permisos:
        assign_perm(permiso.codename,rol,proyecto)
    id_nombre_rol=rol.name.split('_')
    proyecto=Proyecto.objects.get(id_proyecto=int(id_nombre_rol[0]))
    registrarAuditoriaProyecto(request.user,
                               "Se creo el rol :" +str(id_nombre_rol[1]),
                               proyecto.id_proyecto,proyecto.nombre,
                               '---')
    return redirect('gestion:menu')

def modificar_rol_proyecto(request,nombre):
    '''
    Esta funcion es la encargada de modificar los permisos de un  rol en un determinado proyecto, este
    funcion se activa luego de modificar un rol en un proyecto, entoce lo que realiza es busca todos los permisos
    que tiene ahora el nuevo rol actualizado y todos los permisos del viejo rol,entonces verifica aquellos
    nuevos que se agrego y aquellos que se eliminaron y lo actualiza tambien los permisos del viejo rol
    Vale recalcar que el viejo rol es que esta asociado a django gurdian, y el rol actualizado es el de Django

    :param request:
    :param nombre:
    :return:
    '''
    id_proyecto, nombre_rol = nombre.split('_')
    proyecto = Proyecto.objects.get(id_proyecto=id_proyecto)
    rol = Group.objects.get(name=nombre)
    permisos = rol.permissions.all()


    lista_permisos_viejos=get_groups_with_perms(proyecto,attach_perms=True)[rol]
    print('viejos sin borrar',lista_permisos_viejos)

    list_permisos_actual=[]#La lista de permisos actualizados del Rol 'nombre'
    for permiso in permisos:
        list_permisos_actual=list_permisos_actual + [permiso.codename]
    print('actual sin borra',list_permisos_actual)
    '''aca se recorre para saber que permisos actualizar al proyecto'''

    for permiso in lista_permisos_viejos[:]:
        if permiso in list_permisos_actual: #esto ya es lo que el usuario tiene
            list_permisos_actual.remove(permiso) #eliminamos del actual y del viejo
            lista_permisos_viejos.remove(permiso)
    '''Aca son dos iteraciones, el primero es lista_permisos_actual que son los permisos que faltan agregar'''
    for permiso in list_permisos_actual:
        assign_perm(permiso,rol,proyecto)
    '''aca la segunda iteracion que son los permisos que se sacaron del rol, por lo tanto hay que eliminar del rol django guardian'''
    for permiso in lista_permisos_viejos:
       remove_perm(permiso,rol,proyecto)

    print('viejo borrado', lista_permisos_viejos)
    print('actual borrado', list_permisos_actual)

    id_nombre_rol = rol.name.split('_')
    proyecto = Proyecto.objects.get(id_proyecto=int(id_nombre_rol[0]))
    registrarAuditoriaProyecto(request.user,
                               "Se modifico el rol :" + str(id_nombre_rol[1]),
                               proyecto.id_proyecto, proyecto.nombre,
                               '---')
    return redirect('gestion:menu')



from guardian.shortcuts import get_objects_for_user
from guardian.models import *
def validar_rol_fase(permiso,fase,usuario):
    '''
    Esta funcion es la encargada de validar si un usuario tiene un determinado permiso,en una fase especifica
    para ello optiene el nombre del  rol al cual esta asociado el permiso,y ese rol busca en la tabla Fase_ROl para determinar
    si ese rol esta asociado a ese usuario, en la fase en el que se esta trabajando, si el usuario tiene el
    rol se retorna True, en caso contrario se retorna False

    :param permiso:
    :param fase:
    :param usuario:
    :return: Boolean
    '''
    content_type = ContentType.objects.get(model='proyecto')
    per = Permission.objects.get(content_type=content_type.id,codename=permiso)
    roles = GroupObjectPermission.objects.filter(object_pk=fase.id_Proyecto.id_proyecto,permission_id=per.id)
    valor=False
    for rol in roles:
        g=Group.objects.get(id=rol.group_id)
        valor=verifacar_roles_usuario(g,fase,usuario)
        if valor:
            return True
    return False
def verifacar_roles_usuario(rol,fase,usuario):
    '''
    Esta funcion es la encarganda de validar si un usuario tiene un rol especifico en una determinada fase
    si tiene, retorna un True, si no retorna un False
    :param rol:
    :param fase:
    :param usuario:
    :return: Boolean
    '''
    if FASE_ROL.objects.filter(id_fase_id=fase.id_Fase,id_rol_id=rol.id,id_usuario_id=usuario.id).exists():
        print('Si tiene ese rol en esa Fase')
        return True
    return False

def seleccionar_usuario_rol(request,id_fase):
    '''
    Esta funcion es la encargada de listar todos los usuario que existen en el proyecto,de todos los
    listados  se selecciona uno y este usuario seleccionado  es aquel al  cual se le va a asignar o sacar
    roles en una determinada fase(id_fase).
    :param request:
    :param id_fase:
    :return:
    '''
    try:
        fase = Fase.objects.get(id_Fase=id_fase)
    except Fase.DoesNotExist:
        return HttpResponse('solicitud erronea, fase no existe', status=400)

    pk=Fase.objects.get(id_Fase=id_fase).id_Proyecto_id
    proyecto=Proyecto.objects.get(id_proyecto=pk)

    #validar el estado del proyecto
    context = validar_proyecto_cancelado(proyecto.id_proyecto)
    if context != {}:
        messages.error(request, "Ya no se puede trabar en un proyecto cancelado")
        return redirect('gestion:detalles_Proyecto', proyecto.id_proyecto)

    user = request.user  ## USER ACTUAL
    form = Usuario.objects.all()
    registrados = User_Proyecto.objects.all()
    fase=Fase.objects.get(id_Fase=id_fase)
    ##hacer  el if para mostra el mensaje de error si es que el proyecto aun no tiene roles

    if obtener_todos_roles_proyecto(proyecto.id_proyecto) ==[]:
        messages.error(request,"El Proyecto aun no tiene roles, creelos antes de asingar")
        return redirect('gestion:detalles_Proyecto',proyecto.id_proyecto)

    if request.method=='POST':
        some_var=request.POST.getlist('radio')
        return  redirect('gestion:Asignar_Rol_usuario_proyecto',id_Fase=id_fase,id_usuario=some_var[0])

    else:
        if validar_permiso(request.user, "is_gerente", fase.id_Proyecto):  # primero se valida si es gerente en el proyecto actual)
            list = []
            for i in range(form.count()):
                ok = False
                if form[i].id != user.id:  # and form[i].esta_aprobado == True :
                    for x in range(registrados.count()):
                        if registrados[x].proyecto_id == pk:
                            if form[i].id == registrados[x].user_id:
                                ok = True
                if ok:
                    list.append(form[i].id)
            return render(request, 'proyectos/seleccionar_usuario_rol.html',
                          {'form': form, 'list': list, 'pk': pk, "proyectos": proyecto})
        else:
            messages.error(request, "No es gerente de proyecto, por lo tanto no puede asignar roles")
            return redirect('gestion:detalles_Proyecto', proyecto.id_proyecto)


def eliminar_rol_proyecto_usuario(id_fase, listaRoles, usuario,user):
    '''
     Esta funcion es la encargada de sacar los roles de una  fase a un usario en  especifico,
     recibe una lista de roles como parametros, que seria los roles que el gerente no marco en el form al
     momento de asignar el rol a un usuario, de esa lista de roles se verifica aquellos que el usuario tiene,
     si es asi, se le saca el rol en esa fase al usuario.

    :param id_fase:
    :param listaRoles:
    :param usuario:
    :return: None
    '''
    fase=Fase.objects.get(id_Fase=id_fase)
    for rol in listaRoles:
        group = Group.objects.get(name=rol)
        print(id_fase, group.id, usuario.id)
        if FASE_ROL.objects.filter(id_fase_id=id_fase, id_rol_id=group.id, id_usuario_id=usuario.id).exists():
            id_proyecto, nombre_rol = group.name.split('_')
            registrarAuditoriaProyecto(user,
                                       "Removio el rol: " + nombre_rol + " al usuario '" + usuario.username + "'",
                                       fase.id_Proyecto.id_proyecto, fase.id_Proyecto.nombre,
                                       fase.nombre)
            FASE_ROL.objects.get(id_fase_id=id_fase, id_rol_id=group.id, id_usuario_id=usuario.id).delete()


#-----------------------Crear Linea Base-----------------------
def ver_lb(request,pk):
    """
    LISTA LOS REGISTROS DE LA TABLA AUDITORIA PARA UN PROYECTO EN ESPECIFICO
    :param request:
    :param pk: ID DEL PROYECTO DEL CUAL SE LISTARA LA AUDIRORIA
    :return: AUDITORIA.HTML
    """
    proyecto=Proyecto.objects.get(id_proyecto=pk)
    lineaB=LineaBase.objects.filter(proyecto=proyecto)
    Lb=iLB_item.objects.all()

    context={
        'lb':Lb,
        'lineaB':lineaB,
        'proyectos':proyecto,
    }
    return render(request, 'items/ver_lb.html', context)

def CrearLB(request,pk):
    '''
        Esta funncion es la encargada de crear una linea base, para ello recibe el id de la fase en donde se va a crear,
        y hace un filtrado de todos  los items aprobados y que no se encuentren en otra Linea Base
        Se requere el permiso crear_LB, si no tiene se muestra un mensaje de error

    :param request:
    :param pk:
    :return:
    '''

    form = LBForm(request.POST)
    """
    contexto = super(CrearLB, self).get_context_data(**kwargs)
    idfase = self.kwargs.get('pk', None)
    contexto['fase'] = idfase
    #print(idfase)
    ista_items = Item.objects.filter(fase = idfase, estado = 'Aprobado')
    contexto['items'] = lista_items
    """

    idfase = pk
    lista_items = Item.objects.filter(fase=idfase, estado='Aprobado')

    try:
        fase = Fase.objects.get(id_Fase=idfase)
        lista = LB_item.objects.all()
    except:
        lista = None

    if validar_permiso(request.user,"is_gerente",fase.id_Proyecto) or request.user.has_perm('crear_lb',fase.id_Proyecto) and validar_rol_fase('crear_lb',fase,request.user):
        print('tiene el permiso de crear_lb')
    else:
        print('NO tiene el permiso de crear_lb')
        context = {
            "mensaje": "NO SE POSEE EL PERMISO: crear_lb" + " SOLICITE EL PERMISO CORRESPONDINTE PARA REALIZAR LA ACCION",
            "titulo": "SIN PERMISO  ",
            "titulo_b1": "",
            "boton1": "",
            "titulo_b2": "SALIR",
            "boton2": "/detallesFase/"+str(pk),
            }
        return render(request, 'Error.html', context)

    if request.method == 'POST':
        print("entro")
        try:
            ultimaLB = LineaBase.objects.last()
        except:
            ultimaLB = None

        if ultimaLB == None:
            lb = '0'
        else:
            lb = str(ultimaLB.idLB)

        seleccion = request.POST.getlist('checkbox')
        nombrelb = 'LineaBase' + str(int(lb) + 1) + 'Fase' + str(pk)
        p = LineaBase(nombreLB=nombrelb, proyecto=fase.id_Proyecto)
        p.save()
        x = LineaBase.objects.last()

        for seleccion in seleccion:
            item = Item.objects.get(id_item=seleccion)
            p = LB_item(item=item, lb=x)
            p.save()
            registrarAuditoriaProyecto(request.user, "Se ha creado una LB con nombre " + nombrelb,item.fase.id_Proyecto.id_proyecto, item.fase.id_Proyecto.nombre, item.fase.nombre)

        return redirect('gestion:detallesFase',pk)


    listaItems = []


    for i in lista_items:
        ok = True
        for j in lista:
            if i.id_item == j.item.id_item:
                ok = False
                break
        if ok == True:

            listaItems.append(i.id_item)
            print(listaItems)

    print('print ',listaItems)
    item_verificador = Item.objects.last()
    lista=[]
    context={
        'listaitems':listaItems,
        'fase':pk,
        'items':lista_items,
        'form':LBForm,
        'proyectos':fase.id_Proyecto,
        'list':lista
    }



    return render(request, 'items/crear_lb.html', context)


#--------------------Editar Estado de Item------------------

def modificarEstadoItem(request, pk):
    """
    La funcion realiza la labor de modificar el estado de cualquier item, los estados disponibles son:
        - Creado
        - Finalizado
        - Aprobado
        - En revision
    
    :param request: peticion HTTP enviada desde el navegador
    :type request: dict
    :param pk: id de item a ser modificado
    :type pk: int
    :return: retorna un render con los datos del item a ser modificado
    :rtype: form
    """

    form = FormItemFase(request.POST)
    item = Item.objects.get(id_item = pk)

    contexto = {
        'form' : form,
        'item' : item,
    }

    if form.is_valid():
        x=form.cleaned_data
        z=x.get("estado")#### ESTADO SELECCIONADO

        if z == 'Finalizado':
            item.estado = z
            item.save()
            registrarAuditoriaProyecto(request.user, "Se ha cambiado el estado del item " + item.nombre + " a Finalizado ", item.fase.id_Proyecto.id_proyecto, item.fase.id_Proyecto.nombre, item.fase.nombre)

        elif(z == 'Aprobado'):#si la seleccion hecha es aprobar el item

            if validar_permiso(request.user,"is_gerente",item.fase.id_Proyecto) or request.user.has_perm('aprobar_item',item.fase.id_Proyecto) and validar_rol_fase('aprobar_item',item.fase,request.user):# se consulta si posee el permiso de aprobar un item
                print('tiene el permiso de aprobar_item')
            else:
                context = {
                    "mensaje": "NO SE POSEE EL PERMISO: crear_item" + " SOLICITE EL PERMISO CORRESPONDINTE PARA REALIZAR LA ACCION",
                    "titulo": "SIN PERMISO",
                    "titulo_b1": "",
                    "boton1": "",
                    "titulo_b2": "SALIR",
                    "boton2": "/proyectos/",
                }
                return render(request, 'Error.html', context)


            if(item.estado=='Finalizado'): # se consulta si el estado previo del item era Finalizado, caso contrario se lanza un mensaje de error

                item.estado = z
                item.save()
                print('actualizA EN LA BD el estado')
                registrarAuditoriaProyecto(request.user, "Se ha cambiado el estado del item " + item.nombre + " a Aprobado ", item.fase.id_Proyecto.id_proyecto
                                           , item.fase.id_Proyecto.nombre, item.fase.nombre)
            else:
                context = {
                    "mensaje": "EL ITEM DEBE ESTAR FINALIZADO PARA PODER SER APROBADO",
                    "titulo": "ESTADO DEL ITEM ",
                    "titulo_b1": "",
                    "boton1": "" ,
                    "titulo_b2": "Salir",
                    "boton2": "/cambiarEstadoItem/" + str(pk),
                }
                return render(request, 'Error.html', context)

        return redirect('gestion:cambiarEstadoItem', pk)

    return render(request, 'items/cambiarEstadoItem.html', contexto)

def obtener_todos_roles_proyecto(id_proyecto):
    '''
    Esta funcion es la encargada de obtener todos los roles asociado a un proyecto, retorna una lista de roles
    :param id_proyecto:
    :return: Lista
    '''
    rolNombreProyecto = []
    rolesProyecto = Group.objects.all()  # Otengo Todo los roles del Proyecto
    print(id_proyecto)
    for rolProyecto in rolesProyecto:
        id_Proyecto, nombre_rol = rolProyecto.name.split('_')
        if int(id_Proyecto) == id_proyecto:
            rolNombreProyecto = rolNombreProyecto + [rolProyecto.name]  # Todo los roles le agrego a una lista

    print(rolNombreProyecto)
    return rolNombreProyecto


def validar_proyecto_cancelado(id_proyecto):
    proyecto= Proyecto.objects.get(id_proyecto=id_proyecto)
    context={}
    if (proyecto.estado == "CANCELADO"):
        context = {
            "mensaje": "EL Proyecto ya se encuentra cancelado, por lo tanto ya no puede realizar acciones dentro de el: " ,
            "titulo": "PROYECTO CANCELADO",
            "titulo_b1": "",
            "boton1": "",
            "titulo_b2": "Volver a Mis Proyectos",
            "boton2": "/proyectos/",
        }
    return  context
