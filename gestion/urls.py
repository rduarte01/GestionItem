from django.urls import path
from . import views
""""
urlpatterns: LAS URL QUE SE UTILIZARAN EN LA WEB
'' MUESTRA LA PAGINA PRINCIPAL
'logout/' DESLOGUEA 
'perfil/' 
'listarUsuarios/'
"""
urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout),
    path('perfil/',views.perfil),
    path('listarUsuarios/',views.getUsers)
# Create your views here.
]