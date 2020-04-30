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

    ##-----------------test de jesus----------------##
    def test_item_asociado_ti(self):
        '''
        Este test verifica que un tipo de item o este asociado a un item para poder eliminarlo
        :return:
        '''

        tipoItem = mixer.blend('gestion.TipoItem',nombre='pruebaTipoItem')
        item= mixer.blend('gestion.Item',nombre='pruebaItem',ti=tipoItem)
        print(item.ti.id_ti)

        assert Item.validar_ti_item(tipoItem.id_ti),'Falso por que tipo de item no esta asociado a ningun item'

    def test_eliminar_atributo_ti(self):
        '''
        Este test verifica la views eliminar_atributo_ti, validando si el status del metodo http es 200,
        el valor  sera distinto a 200 en caso en que le pasemos un parametro que no exista en la base de
        datos a nuestra funcion
        :return:
        '''
        fase = mixer.blend('gestion.Fase')
        tipoItem=mixer.blend('gestion.TipoItem',fase_id=fase.id_Fase)

        id_ti = tipoItem.id_ti
        path=reverse('gestion:eliminar_atributo_ti',kwargs={'id_ti':id_ti})

        request=RequestFactory().get(path)
        request.user=mixer.blend('auth.User')
        response=eliminar_atributo_ti(request,id_ti=id_ti)

        assert response.status_code==200,'Error, Respuesta http response distinto a 200,la solicitud estuvo incorrecta'

    def test_eliminar_tipo_item(self):
        '''
        Este test verifica la views eliminar_tipo_item, validando si el status del metodo http es 200, el valor
        sera distinto a 200 en caso en que le pasemos un parametro que no exista en la base de datos a nuestra funcion
        :return:
        '''
        fase = mixer.blend('gestion.Fase')
        tipoItem=mixer.blend('gestion.TipoItem',fase_id=fase.id_Fase)
        id_ti=tipoItem.id_ti #343434
        path=reverse('gestion:eliminar_tipo_item',kwargs={'id_ti':id_ti})
        request=RequestFactory().get(path)
        request.user=mixer.blend('auth.User')
        response=eliminar_tipo_item(request,id_ti=id_ti)

        assert response.status_code==200,'Error, Respuesta http response distinto a 200,la solicitud estuvo incorrecta'

    def test_agregar_atributo_ti(self):
        '''
        Este test verifica la views eliminar_atributo_ti, validando si el status del metodo http es 200
        :return:
        '''
        fase = mixer.blend('gestion.Fase')
        tipoItem=mixer.blend('gestion.TipoItem',fase_id=fase.id_Fase)
        id_ti=tipoItem.id_ti #343434
        path=reverse('gestion:agregar_atributo_ti',kwargs={'id_ti':id_ti})
        request=RequestFactory().get(path)
        request.user=mixer.blend('auth.User')
        response=agregar_atributo_ti(request,id_ti=id_ti)
        assert response.status_code==200,'Error, Respuesta http response distinto a 200,la solicitud estuvo incorrecta'

    def test_editar_ti(self):
        '''
        Este test verifica la views eliminar_atributo_ti, validando si el status del metodo http es 200
        :return:
        '''
        fase = mixer.blend('gestion.Fase')
        tipoItem=mixer.blend('gestion.TipoItem',fase_id=fase.id_Fase)
        id_ti=tipoItem.id_ti #343434
        path=reverse('gestion:editar_ti',kwargs={'id_ti':id_ti})
        request=RequestFactory().get(path)
        request.user=mixer.blend('auth.User')
        response=editar_ti(request,id_ti=id_ti)
        assert response.status_code==200,'Error, Respuesta http response distinto a 200,la solicitud estuvo incorrecta'

    def test_Asignar_Rol_usuario_proyecto(self):
        fase = mixer.blend('gestion.Fase',nombre='fase1')
        usuario=mixer.blend('auth.User',username='usuarioPruba')

        id_fase=fase.id_Fase
        #id_fase=434343
        id_usuario=usuario.id

        path = reverse('gestion:Asignar_Rol_usuario_proyecto', kwargs={'id_Fase': id_fase,'id_usuario':id_usuario})
        request = RequestFactory().get(path)
        request.user = mixer.blend('auth.User')
        response = Asignar_Rol_usuario_proyecto(request, id_Fase=id_fase,id_usuario=id_usuario)
        assert response.status_code==200,'Error, Respuesta http response distinto a 200,la solicitud estuvo incorrecta'

    def test_validar_rol_fase(self):
        fase = mixer.blend('gestion.Fase', nombre='fase1')
        usuario = mixer.blend('auth.User', username='usuarioPruba')

        rol1 = mixer.blend('auth.Group', name='rol1')
        rol2 = mixer.blend('auth.Group', name='rol2')
        FASE_ROL.objects.create(id_fase_id=fase.id_Fase,id_rol_id=rol1.id,id_usuario_id=usuario.id)

        assert verifacar_roles_usuario(rol1,fase,usuario),'Error , Falso por que el usuario no tiene el rol para esa fase pasada como parametro '
