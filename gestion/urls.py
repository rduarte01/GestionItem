from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout),
    path('perfil/',views.perfil),
    path('listarUsuarios/',views.getUsers),
    path('menu/', views.menu)
]