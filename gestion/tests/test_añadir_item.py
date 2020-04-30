from django.urls import reverse, resolve
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser,Permission
from gestion.views import *
from gestion.models import *
from mixer.backend.django import mixer
from django.test import TestCase
import pytest


@pytest.mark.django_db
class Test_Crear_Item(TestCase):

    def test_item_create(self):
        proyecto = Proyecto.objects.create(
            nombre="p1",
            descripcion='.',
            #       estado='CREADO',
            estado='INICIADO',

        )
        fase = Fase.objects.create(
            nombre='f1',
            descripcion='.',
            estado='Abierta',
            id_Proyecto=proyecto
        )
        #    fase=Fase.objects.create(
        Fase.objects.create(
            nombre='f2',
            descripcion='.',
            estado='Abierta',
            id_Proyecto=proyecto
        )

        path = reverse('gestion:crearItem', kwargs={'Faseid': fase.id_Fase})
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)

        id_fase=fase.id_Fase
        #id_fase=999 #no existe
        response = crearItem(request, Faseid=id_fase)

        assert response.status_code == 200 ,"Id de la fase enviada como parametro invalida"


    def test_fase_uno_validation(self):
        proyecto=mixer.blend('gestion.Proyecto',nombre='p1')

        fase1=mixer.blend('gestion.Fase',nombre='f1',id_Proyecto=proyecto)
        fase=mixer.blend('gestion.Fase',nombre='f2',id_Proyecto=proyecto)

        mixer.blend('gestion.Fase',nombre='f3',id_Proyecto=proyecto)

        mixer.blend('gestion.Item',nombre='i1',fase=fase1) #restriccion


        fases=Fase.objects.filter(id_Proyecto=proyecto)


        assert fase1SinItems(fases,fase) != True, "La fase anterior sin items, no se podra relacionar con la primera fase"


    def test_ti_en_fase(self):
        proyecto=mixer.blend('gestion.Proyecto',nombre='p1')
        fase=mixer.blend('gestion.Fase',nombre='f1',id_Proyecto=proyecto)

        mixer.blend('gestion.TipoItem',nombre='TI1',fase=fase)#restriccion

        assert hayTiFase(fase) != True, "No hay Ti en la fase por ende no se puede crear item"

    def test_lista_ti(self):
        proyecto=mixer.blend('gestion.Proyecto',nombre='p1')
        fase=mixer.blend('gestion.Fase',nombre='f1',id_Proyecto=proyecto)

        mixer.blend('gestion.TipoItem', nombre='ti', fase=fase) # restriccion

        path = reverse('gestion:agg_listar_tipo_item', kwargs={'Fase': fase.id_Fase})
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)

        response = agg_listar_tipo_item(request, fase.id_Fase)

        assert response.status_code == 200, "Id de la fase enviada como parametro invalida, no se puede crear item sin TI"

    def test_atributos(self):
        proyecto=mixer.blend('gestion.Proyecto',nombre='p1')
        fase=mixer.blend('gestion.Fase',nombre='f1',id_Proyecto=proyecto)
        ti=mixer.blend('gestion.TipoItem', nombre='ti', fase=fase)

        mixer.blend('gestion.Atributo',ti=ti)  # restriccion

        path = reverse('gestion:aggAtributos', kwargs={'idTI': ti.id_ti})
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)

        id_ti=ti.id_ti
        #id_ti=9999

        response = aggAtributos(request, id_ti)

        assert response.status_code == 200, "Id del TI invalida, no se puede crear item si su TI no tiene atributos"


    def test_relacion_item(self):
        proyecto=mixer.blend('gestion.Proyecto',nombre='p1')
        fase1=mixer.blend('gestion.Fase', nombre='f1', id_Proyecto=proyecto)
        fase2=mixer.blend('gestion.Fase', nombre='f2', id_Proyecto=proyecto)
        fase3=mixer.blend('gestion.Fase', nombre='f3', id_Proyecto=proyecto)

        item=mixer.blend('gestion.Item',nombre='i1',fase=fase1)

        path = reverse('gestion:relacionarItem', kwargs={'id_proyecto': proyecto.id_proyecto,'id_item': item.id_item})
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)

        response = relacionarItem(request, proyecto.id_proyecto,item.id_item)

        assert response.status_code == 200, "Id del item o proyecto enviado como parametro invalida, no se puede crear item sin relaciones"

    def test_relacion_lista_item(self):
        proyecto=mixer.blend('gestion.Proyecto',nombre='p1')
        fase1=mixer.blend('gestion.Fase', nombre='f1', id_Proyecto=proyecto)
        fase2=mixer.blend('gestion.Fase', nombre='f2', id_Proyecto=proyecto)
        fase3=mixer.blend('gestion.Fase', nombre='f3', id_Proyecto=proyecto)

        proyecto2=mixer.blend('gestion.Proyecto',nombre='p1')
        fase4=mixer.blend('gestion.Fase', nombre='f1', id_Proyecto=proyecto2)

        item=mixer.blend('gestion.Item',nombre='i1',fase=fase1)#restriccion
        fases=Fase.objects.filter(id_Proyecto=proyecto)

        lista_items_relacion(item, fases,proyecto.id_proyecto,item.id_item)
        listVacia=[]
        assert lista_items_relacion(item, fases,proyecto.id_proyecto,item.id_item)==listVacia , "El item no pertenece a las fases del proyecto enviado"
