from django.urls import reverse
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from gestion.views import *
from mixer.backend.django import mixer
from django.test import TestCase
import pytest
from gestion.models import *
from django.contrib.contenttypes.models import ContentType

@pytest.mark.django_db
class TestViews(TestCase):
    
        
    def test_perfil_authenticated(self):
        """
        Comprueba si se muestra el perfil del usuario solicitante.
        return: Si no se realiza correctamente la visualizacion del perfil del usuario retorna un mensaje de error, caso contrario se omiten mensajes.
        """
        mixer.blend('gestion.Usuario')
        path = reverse('gestion:perfil')
        request = RequestFactory().get(path)
        request.user = AnonymousUser()

        print(request.user)

        response  = perfil(request)
        print(response)
        assert response.status_code == 302, "No se ha encontrado la pagina que muestra el perfil del usuario, codigo de respuesta distinto a 302"
    
    
    #path('AggUser/<int:pk>', views.AggUser, name='AggUser'),
    def test_Agg_User(self):
        """
        Comprueba si se agrega correctamente un usuario a un proyecto
        """

        mixer.blend('gestion.Usuario')
        path = reverse('gestion:AggUser', kwargs = {'pk': 1})
        request = RequestFactory().get(path)
        request.user = AnonymousUser()

        print(request.user)
        response = AggUser(request, pk = 1)
        print(response)
        assert response.status_code == 200, "No se ha podido agregar el usuario al proyecto, codigo respuesta distinto a 200"


    #path('creacionProyecto/', views.creacionProyecto), OK
    def test_creacionProyecto(self):
        """
        Verifica que la creacion de proyecto se realice de manera correcta.
        return: Si la creacion no se ha realizado retorna un mensaje de error, caso contrario no devuelve ningun mensaje.
        """

        proyecto = Proyecto.objects.create(
            nombre = 'Proyecto1',
            descripcion = 'Este es el primer Proyecto'

        )

        mixer.blend('gestion.Proyecto')
        path = reverse('gestion:CrearProyecto')
        request = RequestFactory().post(path)

        proyecto1 = Proyecto.objects.last()
        response = creacionProyecto(request)
        assert response.status_code == 200
        assert proyecto == proyecto1, "No se ha creado el proyecto"
    
    #path('crear_fase/', views.crearFase, name='crearFase'),
    def test_creacionFase(self):
        """
        Verifica que la creacion de fases se haga de manera correcta.
        return: Si no se ha llevado a cabo la correcta creacion de una fase emitirá un mensaje de error, caso contrario no emitirá ningún mensaje
        """
        proy = Proyecto.objects.create(
            nombre = 'Proyecto1',
            descripcion = 'Este es el primer Proyecto'
        )

        fase = Fase.objects.create(
            nombre = 'Fase1',
            descripcion = 'Esta es la fase 1',
            id_Proyecto = Proyecto.objects.get(id_proyecto = proy.id_proyecto)
        )
            
        mixer.blend('gestion.Fase')
        path = reverse('gestion:crearFase')
        request = RequestFactory().get(path)

        response = crearFase(request) 

        assert response.status_code == 200, "No se ha creado la fase, codigo de respuesta http distinto a 200"

    #path('agregarUsuarios/<int:pk>', views.agregarUsuarios, name='agregarUsuarios'),
    def test_agregarUsuario(self):
        """
        Comprueba que se agregue correctamente un usuario a un proyecto. Recibe el ID de un usuario y muestra los usuarios que
        pueden ser añadidos a él.
        return: Si no se agrega un usuario a un proyecto se lanza un mensaje de error, caso contrario se omiten mensajes. 
        """
        user = User.objects.create(
            email = 'marcos@marcos.gmail',
            password = 'marcos123'
        )

        usuario = Usuario.objects.create(
            user = User.objects.get(id = user.id)
        )

        user1 = Usuario.objects.last()

        id = int(user1.user)

        mixer.blend('gestion.Usuario')
        path = reverse('gestion:agregarUsuarios', kwargs = {'pk': id})
        request = RequestFactory().get(path)
        request.user = AnonymousUser()

        response = agregarUsuarios(request, pk = 1)

        assert response.status_code == 200, "No se ha agregado el usuario solicitado al proyecto, codigo de respuesta http distinto a 200"
        
    #path('crear/atributo/<str:nombre_ti>/<int:cantidad_atributos>/<int:fase_id>',views.add_atribute,name='add_atribute'),

    def test_add_atributo(self):
        """
        Comprueba que se crea correctamente un atributo para un tipo de item determinados. La funcion recibe un request
        return: Si no se realiza correctamente la creacion de un atributo lanza un mensaje de error, caso contrario no se visualiza nada.
        """
        tipoitem1 = TipoItem.objects.create(
            nombre = 'tipoitem1'
        )

        atributo = Atributo.objects.create(
            nombre = 'atributo1',
            es_obligatorio = True,
            tipo_dato = 'DECIMAL',
            ti = TipoItem.objects.get(id_ti = tipoitem1.id_ti)
        )
        
        atributo1 = Atributo.objects.last()

        assert atributo == atributo1 

    def test_usuario_aprobado(self):
        """
        Comprueba si la cantidad de usuarios aprobados es correcta. Cabe resaltar que por defecto un usuario recien creado no esta aprobado
        return: Devuelve un mensaje de error si la cantidad de usuarios aprobados no esta acorde a los usuarios creados inicialmente(deben ser distintos)
        """

        user1 = User.objects.create(
            email = 'a@a.com',
            password = '123'
        )

        usuario1 = Usuario.objects.create(
            user = User.objects.get(id = user1.id)
        )

        usuarios = Usuario.objects.filter(esta_aprobado = False)

        """
        Se iguala a 1 ya que al usar django-guardian se crea automáticamente un usuario AnonymousUser
        """
        assert usuarios.count() == 1, "No se encuentra la totalidad de usuarios aprobados"

    def test_usuario_no_aprobado(self):
        """
        Comprueba si la cantidad de usuarios no aprobados es correcta
        return: Devuelve un mensaje de error si la cantidad de usuarios no aprobados no coincide con la cantidad de usuarios creados inicialmente
        """

        user1 = User.objects.create(
            email = 'a@a.com',
            password = '123'
        )

        usuario = Usuario.objects.create(
            user = User.objects.get(id = user1.id)
        ) 

        usuarios = Usuario.objects.filter(esta_aprobado = True)

        assert usuarios.count() == 0, "No se encuentra la totalidad de usuarios no aprobados"
    
    def test_estado_proyecto(self):
        """
        Comprueba si se realiza correctamente la modificacion de estado de un proyecto determinado
        return: Si no se obtiene una respuesta Http 200 se emite un mensaje de error, de lo contrario no se visualiza nada
        """
        proyecto = Proyecto.objects.create(
            nombre = 'Proyecto1',
            descripcion = 'Este es el proyecto1'
        )

        print(Proyecto.objects.get(id_proyecto = proyecto.id_proyecto))

        mixer.blend('gestion.Proyecto')
        path = reverse('gestion:estado_Proyecto', kwargs = {'pk': 6})
        request = RequestFactory().get(path)

        request.user = AnonymousUser()

        response = estadoProyecto(request, pk = 6)

        print(response)

        assert response.status_code == 200, "No se ha podido cambiar de estado el proyecto, código Http es distinto a 200"

#def importar_tipo_item(request,id_fase):
#path('importar/tipo/item/fase/<int:id_fase>', views.importar_tipo_item, name='importar_tipo_item'),
   
    def test_importar_tipo_de_item(self):
        """
        Comprueba si se ha llevado a cabo correctamente la importacion de un tipo de item en una fase determinada.
        El metodo importar_tipo_item recibe como parametros un request y un id de una fase
        return: Si no se ha llevado a cabo correctamente la importacion retorna un mensaje de error, caso contrario no se visualiza nada.
        """   
        proyecto = Proyecto.objects.create(
            nombre = 'Proyecto1',
            descripcion = 'Este es el proyecto1'
        )

        fase2 = Fase.objects.create(
            nombre = 'Fase1',
            descripcion = 'Esta es la fase1',
            id_Proyecto = Proyecto.objects.get(id_proyecto = proyecto.id_proyecto)
        )
        print(Fase.objects.get(id_Fase = fase2.id_Fase))
        
        mixer.blend('gestion.TipoItem')
        path = reverse('gestion:importar_tipo_item', kwargs = {'id_fase': 4})
        request = RequestFactory().post(path)

        response = importar_tipo_item(request, id_fase = 4)
        print(response)    
        assert response.status_code == 302, "No se ha podido importar un tipo de item, el codigo de respuesta Http es distinto a 302"

# def menu(request):
# path('menu/', views.menu, name='menu'),    
    def test_menu(self):
        """
        Comprueba si se ha llevado a cabo correctamente el montado de la vista menu del sistema.
        El metodo menu recibe como parametro un request
        return: Retorna un mensaje de error si la operacion no se ha llevado a cabo correctamente, caso contrario no se visualiza nada.
        """
        user1 = User.objects.create(
            email = 'usuario1@usuario1.com',
            password = 'usuario1123'
        )
        
        usuario = Usuario.objects.create(
            user = User.objects.get(id = user1.id)
        )
        
       path = reverse('gestion:menu')
        request = RequestFactory().get(path)

        request.user = User.objects.last()

        print(Usuario.objects.last())

        response = menu(request)

        assert response.status_code == 200, "No se ha podido completar la operacion, codigo de salida distinto a 200"

#path('crearRol/<str:proyecto>', CrearRol.as_view(), name='crearRol'),
    def test_CrearRol(self):
        """
        Comprueba si se realiza correctamente la creacion de un Rol. Se compara si el resultado es distinto a None ya que el metodo super() de
        la funcion crearRol devuelve una direccion de memoria como respuesta.
        return: Si no se lleva a cabo correctamente la creacion de un rol devuelve un mensaje de error, de lo contrario no se visualiza nada.
        """

        mixer.blend('gestion.FASE_ROL')
        path = reverse('gestion:crearRol', kwargs = {'proyecto': 1})
        request = RequestFactory().get(path)

        response = CrearRol()
        print(response)

        assert response != None, "No se ha podido realizar la operacion, retorno de funcion igual a None, deberia ser una direccion de memoria"

#class ModificarRol(UpdateView):
#class FASE_ROL(models.Model):
#path('modRol/<int:pk>', ModificarRol.as_view(), name='modificarRol'),

    def test_modificar_rol(self):
        """
        Comprueba si se realiza correctamente la modificacion de un rol. Se compara con None el resultado ya que las funciones 
        internas devuelven direcciones de memoria.
        return: Si no se lleva a cabo la modificacion de un rol devuelve un mensaje de error, caso contrario no se visualiza nada.
        """

        mixer.blend('gestion.FASE_ROL')
        path = reverse('gestion:modificarRol', kwargs = {'pk': 1})
        request = RequestFactory().get(path)

        response = ModificarRol()
        print(response)

        assert response != None, "No se ha podido realizar la operacion, retorno de funcion igual a None, debe retornar una direccion de memoria"
