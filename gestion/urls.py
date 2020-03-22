from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('menu/logout/', views.logout),
    path('menu/perfil/',views.perfil),
    path('listarUsuarios/',views.getUsers),
    path('menu/is_admin', views.menu,name='menu'),
    path('creacionProyecto/', views.creacionProyecto,name='creacionProyecto'),
    path('Contactos/', views.Contactos),
    path('enEspera/',views.verSolicitudesenEspera),
    path('crear/TipoItem',views.tipo_item_views_create,name='tipo_item_views_create'),
    path('crear/atributo',views.add_atribute,name='add_atribute')
]


