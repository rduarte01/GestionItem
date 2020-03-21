from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('menu/logout/', views.logout),
    path('menu/perfil/',views.perfil),
    path('listarUsuarios/',views.getUsers),
    path('menu/', views.menu),
    path('creacionProyecto/', views.creacionProyecto),
    path('Contactos/', views.Contactos),
    path('enEspera/',views.verSolicitudesenEspera),
]


