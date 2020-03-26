from django.urls import path
from .views import crearFase, listar_auditoria, listar_usuarios_registrar,listar_proyectos
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('menu/logout/', views.logout),
    path('menu/perfil/',views.perfil),
    path('listarUsuarios/',views.getUsers),
    path('menu/', views.menu, name='menu'),
    path('creacionProyecto/', views.creacionProyecto),
    path('Contactos/', views.Contactos),
    path('enEspera/',views.verSolicitudesenEspera),
    path('crear_fase/', views.crearFase, name='crearFase'),
    path('auditoria/', listar_auditoria),
    path('AggUser/', listar_usuarios_registrar),
    path('proyectos/', listar_proyectos),

]


