from django.urls import reverse
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from gestion.views import perfil, agregarUsuarios, estadoProyecto, importar_tipo_item, menu, tipo_item_views_create, CrearRol, ModificarRol, AggUser, creacionProyecto, crearFase, modificarEstadoItem, CrearLB
from mixer.backend.django import mixer
from django.test import TestCase
import pytest
from gestion.models import Proyecto, Fase, Atributo, TipoItem, Usuario, FASE_ROL, Item

@pytest.mark.django_db
class TestViews(TestCase):

#path('cambiarEstadoItem/<int:pk>/', views.modificarEstadoItem, name = 'cambiarEstadoItem'),
#def modificarEstadoItem(request, pk):
#class Item(models.Model):
    def test_modificarEstadoItem(self):
        """
        Comprueba si se realiza correctamente la modificacion de estado de un item. Si ocurre un error, se visualiza en pantalla un mensaje
        de que no se pudo modificar el estado del item en cuestion.
        return: Retorna un mensaje de error si algo salió mal, caso contrario no se visualiza nada.
        """
        print('------------')
        #user = User.objects.create(
         #   email = 'usuario1@usuario1.com',
          #  password = 'usuario1'
        #)

        #print(user)

        #usuario = Usuario.objects.create(
         #   user = User.objects.last()
        #)

        #print(usuario)

        #proyecto = Proyecto.objects.create(
         #   nombre = 'Proyecto1',
          #  descripcion = 'Este es el proyecto1',
           # users = Usuario.objects.last()
        #)

        #print(proyecto)

        #fase = Fase.objects.create(
         #   nombre = 'Fase1',
          #  descripcion = 'Esta es la fase1',
           # id_Proyecto = Proyecto.objects.get(id_proyecto = proyecto.id_proyecto)
        #)

        #print(fase)

        #tipoitem = TipoItem.objects.create(
         #   nombre = 'TipoItem1',
          #  fase = Fase.objects.last()
        #)

        #item = Item.objects.create(
         #   nombre = 'Item 1',
          #  descripcion  = 'Es el item numero 1',
           # costo = 2,
            #ti = TipoItem.objects.last(),
            #fase = Fase.objects.last(),
            #actual = True
        #)

        #item_a_enviar = int(Item.objects.last().id_item)

        proyecto1 = mixer.blend('gestion.Proyecto', nombre = 'proyecto1')
        fase1 = mixer.blend('gestion.Fase', nombre = 'fase1', id_Proyecto = proyecto1)
        tipoitem1 = mixer.blend('gestion.TipoItem', nombre = 'proyecto1', fase = fase1)
        item1 = mixer.blend('gestion.Item', nombre = 'tipoitem1', ti = tipoitem1, fase = fase1)
        iditem = item1.id_item
        path = reverse('gestion:cambiarEstadoItem', kwargs = {'pk': iditem})
        request = RequestFactory().get(path)

        response = modificarEstadoItem(request, iditem)
        #print(response)

        assert response.status_code == 200, 'Codigo HTTP distinto a 200'

#path('crearLB/<int:pk>/', CrearLB.as_view(), name = 'crearLB'),
#class CrearLB(CreateView):
#class LineaBase(models.Model):
    def test_crearLB(self):
        """
        Comprueba si se realiza correctamente la creacion de una Linea Base en una fase determinada. Muestra un mensaje de error si
        no se pudo realizar la accion.
        return: Muestra un mensaje de error si algo salió mal, caso contrario no se muestra ningún mensaje
        """
        proyecto1 = mixer.blend('gestion.Proyecto', nombre = 'proyecto1')
        fase1 = mixer.blend('gestion.Fase', nombre = 'fase1', id_Proyecto = proyecto1)
        tipoitem1 = mixer.blend('gestion.TipoItem', nombre = 'proyecto1', fase = fase1)
        item1 = mixer.blend('gestion.Item', nombre = 'tipoitem1', ti = tipoitem1, fase = fase1)
        idfase = fase1.id_Fase
        path = reverse('gestion:crearLB', kwargs = {'pk': idfase})
        request = RequestFactory().get(path)
        request.user=mixer.blend('auth.User')
        response = CrearLB(request,idfase)
        #print(response)

        assert response != None, "No se pudo crear la Linea Base solicitada, el metodo retorna un objeto tipo None"