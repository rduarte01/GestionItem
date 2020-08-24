from django.contrib import messages
from urllib import request

from django.core.mail import EmailMessage
from time import strftime, gmtime

from django.shortcuts import  render,redirect
from gestion.models import *
from django.contrib.auth.models import User
import dropbox
TOKEN="PmyFRnnhTbYAAAAAAAAAATzqHtLq9zKgZw5oSajE3ClcBDVwOi7vSYxi5todZcsv"
"""TOKEN DE DROPBOX PARA REALIZAR LA CONEXION"""

def validar_permiso(user,permiso, proyecto):
    '''
        Esta funcion permite validar el permiso de un usuario para un proyecto en especifico,  el nombre del
        permiso es recibido como segundo parametro en la funcion y el proyecto como tercer parametro  ,
        si el usuario tiene  el permiso  para  el  proyecto recibido entonces la funcion retornara True,
        en caso Contrario retornara False

    :param user:
    :param permiso:
    :param proyecto:
    :return:
    '''
    if user.has_perm(permiso,proyecto):
        return True
    return False

#RUBEN
def registrarAuditoria(user,accion):
    """FUNCION QUE REGISTRA EN LA  TABLA AUDITORIA LO QUE SE REALIZA EN EL SISTEMA"""
    showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    p = Auditoria(usuario= user,fecha=showtime, accion=accion)###### FALTA ARREGLAR USER
    p.save()

def listar_auditoria(request):
    """ LISTA LOS REGISTROS DE LA TABLA AUDITORIA PARA EL SISTEMA"""
    auditoria = Auditoria.objects.all()
    proyectos=Proyecto.objects.get(id_proyecto=1)

    context={
        'auditoria':auditoria,
        'proyectos': proyectos

    }
    return render(request, 'Menu/auditoriaSistema.html', context)

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

    proyectos = Proyecto.objects.get(id_proyecto=pk)
    if validar_permiso(request.user, "is_gerente",proyectos) == False:  # primero se valida si es gerente en el proyecto actual)
        messages.error(request,' No eres gerente de proyecto, por lo tanto no puedes desvincular usuarios')
        return redirect('gestion:UsersProyecto', pk)

    if usersComite!=None:
        for id in usersComite:
            usuario=User.objects.get(id=id.id_user)
            if(usuario.id == pk_user ):
                messages.error(request,'EL USUARIO PERTENECE AL COMITE DE CAMBIO POR ENDE NO PODRA DESVINCULARLO DEL PROYECTO, YA QUE LA CANTIDAD DE USUARIOS DEL COMITE QUEDARIA PAR, FAVOR DESVINCULAR DEL COMITE Y LUEGO DEL PROYECTO')
                return redirect('gestion:UsersProyecto',pk)

    instanceUser = User_Proyecto.objects.filter(proyecto_id = pk, user_id = pk_user)
    usuario = User.objects.get(id=pk_user)
    registrarAuditoriaProyecto(request.user, "Desvinculo del proyecto al usuario: " + str(usuario.username),
                               proyectos.id_proyecto, proyectos.nombre, "")

    instanceUser.delete()

    return redirect('gestion:UsersProyecto',pk)

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


def fase1SinItems(fases,fase):
    """
    Verifica si la fase en la que se quiere crear el item podra tener relacion con la primera fase

    :param fases: lista de fases
    :param fase: la fase en la que se quiere crear el item
    :return: true si no tiene relacion con fase 1, false caso contrario
    """
    cont = 1
    print("fases: ",fases)
    print("fase: ",fase)
    if (fases.count() != 1):  # si no es de la primera fase
        print("el proyecto posee ",fases.count()," fases")
        for faseSIG in reversed(fases):
            print("recorrido ",faseSIG)
            if (faseSIG == fase):  # se verifica que fase es
                print("se encontro fase buscada: ",fase)
                print("cont= ",cont)
                break
            cont += 1
    else:
        print("solo hay una fase sale de la funcion")
        return False

    if (cont != 1):
        print("se ingresa proque cont no es 1")
        item_fase=Item.objects.filter(fase=fase.id_Fase-1)
        print("items de la fase anterior ",item_fase)
        if(item_fase.count() == 0):
            print("no hay item retorna true")
            return True
    print("hay items en la fase anterior retorna false")
    return False


def hayTiFase(fase):
    """
    Verifica si hay TI en la fase
    :param fase: fase en donde se creara el item
    :return: true si no hay, caso contrario false
    """
    try:
        ti = TipoItem.objects.filter(fase=fase)
    except:
        ti = None

    if (ti == None or ti.count() == 0):  # muestra mensaje de error si no hay TI no se puede crear item
        return True
    return False

def itemCancelado(request,pk):
    """
    METODO PARA CANCELAR UN ITEM
    :return: REDIRIGE AL MENU PRINCIPAL
    """

    try:
        x = Item.objects.get(id_item=pk)
        fase = x.fase.id_Fase
    except:
        context = {
            "mensaje": "EL ITEM YA NO EXISTE ",
            "titulo": "ITEM",
            "titulo_b1": "",
            "boton1": "",
            "titulo_b2": "Salir",
            "boton2": "/proyectos/",
        }
        return render(request, 'Error.html', context)

    try:
        ruta = f'/{x.fase.id_Proyecto.id_proyecto}/{x.id_item}'
        dbx = dropbox.Dropbox(TOKEN)
        dbx.files_delete(ruta)
        print("borro archivos adjuntos")
    except:
        print("sin archivos adj. que borrar")
    x.delete()

    instanceItem = Atributo_Item.objects.filter(id_item = x)

    for i in instanceItem:
        i.delete()

    return  redirect("gestion:detallesFase",fase)


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
    fases = Fase.objects.filter(id_Proyecto=proyecto).order_by('id_Fase')
    todosItems = Item.objects.filter(fase=fases[0],actual=True)  # todos los items de la primera fase

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

    for id in some_var:
        if(str(id)==str(item.id_item)):######preguntar si es de otra fase si no se puede desde la misma porque --->apunta al contrario
            return True

    for relaciones in relaciones:

        try:
            instanceItem= Item.objects.get(id_item=relaciones.fin_item, actual=True)
        except:
            instanceItem =None
        if instanceItem:
            if(busqueda(instanceItem,id_item,some_var)==True):
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

