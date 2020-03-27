from django.urls import path
from .views import crearFase, listar_auditoria, listar_usuarios_registrar,listar_proyectos, proyectoCancelado
from . import views
from .views import VerSolicitudesEspera, ActualizarUser, CrearRol

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/logout/', views.logout,name='logout'),
    path('menu/perfil/',views.perfil,name='perfil'),
    path('listarUsuarios/',views.getUsers,name='getUser'),
    path('menu/', views.menu, name='menu'),
    path('creacionProyecto/', views.creacionProyecto),
    path('Contactos/', views.Contactos,name='Contactos'),
    path('enEspera/',views.verSolicitudesenEspera),
    path('crear_fase/', views.crearFase, name='crearFase'),
    path('auditoria/', listar_auditoria),
    path('AggUser/', listar_usuarios_registrar),
    path('proyectos/', listar_proyectos),
    path('cancelado/', proyectoCancelado),
    path('crear/TipoItem',views.tipo_item_views_create,name='tipo_item_views_create'),
    path('crear/atributo/<str:nombre_ti>/<int:cantidad_atributos>',views.add_atribute,name='add_atribute'),
    path('listar/usuarios/aprobados',views.ver_usuarios_aprobados,name='ver_usuarios_aprobados'),
    path('getUser/<int:pk>',views.get_user,name='get_user')
]


