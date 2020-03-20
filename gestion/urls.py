from django.urls import path
from . import  views
urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout),
    path('perfil/',views.perfil),
    path('listarUsuarios/',views.getUsers),
   path('crearProyecto',views.crear_Proyecto)
# Create your views here.
]