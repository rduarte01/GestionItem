from django.urls import path
from . import views
from .views import VerSolicitudesEspera, ActualizarUser, VerPermisos

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/logout/', views.logout),
    path('menu/perfil/',views.perfil),
    path('listarUsuarios/',views.getUsers),
    path('menu/', views.menu,name='menu'),
    path('creacionProyecto/', views.creacionProyecto, name= 'crearProyecto'),
    path('Contactos/', views.Contactos),
    path('enEspera/',VerSolicitudesEspera.as_view(), name="listaDeEspera"),
    path('permisos/',VerPermisos.as_view(), name="listaDePermisos"),
    path('crear/TipoItem',views.tipo_item_views_create,name='tipo_item_views_create'),
    path('crear/atributo',views.add_atribute,name='add_atribute'),
    path('getUser/<int:pk>', ActualizarUser.as_view(),name='get_user'),

]


