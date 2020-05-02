from django.urls import reverse, resolve
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser,Permission
from gestion.views import *
from gestion.models import *
from mixer.backend.django import mixer
from django.test import TestCase
import pytest


@pytest.mark.django_db
class Test_comite(TestCase):

    def test_AggComite(self):
        proyecto=mixer.blend('gestion.Proyecto',nombre='p1')

        path = reverse('gestion:AggComite', kwargs={'pk': proyecto.id_proyecto})
        request = RequestFactory().get(path)
        request.user = mixer.blend('auth.User')

        mixer.blend('gestion.User_Proyecto', proyecto_id=proyecto.id_proyecto)


        id=proyecto.id_proyecto
        #id=999
        response = AggComite(request,  id)

        assert response.status_code == 200, "Id del proyecto no valido, no existe dicho proyecto"
