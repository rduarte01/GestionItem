from django.urls import path
from . import  views
urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout, name = 'logout'),
    path('perfil/',views.perfil, name = 'perfil'),
    path('listarUsuarios/',views.getUsers, name = 'getUser')
# Create your views here.
]