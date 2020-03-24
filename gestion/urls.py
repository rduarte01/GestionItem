from django.urls import path
from . import views
from .views import crearFase

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout),
    path('perfil/',views.perfil),
    path('listarUsuarios/',views.getUsers),
    path('crear_fase/', views.crearFase)

# Create your views here.

]