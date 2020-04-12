from django.urls import path
from .views import crearFase, listar_auditoria,listar_proyectos, proyectoCancelado
from . import views
from .views import estadoProyecto,detallesProyecto,UsersProyecto,desvinculacionProyecto,ModificarRol,VerRoles,agregarUsuarios, VerUsersEnEspera, ActualizarUser, CrearRol, crearItem,agg_listar_tipo_item,aggAtributos,relacionarItem,detallesFase,listar_relaciones,listar_atributos,itemCancelado,comite,AggComite,desvinculacionComite


urlpatterns = [
    path('', views.index, name='index'),
    path('menu/logout/', views.logout,name='logout'),
    path('menu/perfil/',views.perfil,name='perfil'),
    path('menu/', views.menu, name='menu'),
    path('creacionProyecto/', views.creacionProyecto, name='CrearProyecto'),
    path('Contactos/', views.Contactos,name='Contactos'),
    #path('enEspera/',views.verSolicitudesenEspera),
    path('crear_fase/<int:nroFase>', views.crearFase, name='crearFase'),
    path('auditoria/', listar_auditoria, name='auditoria'),
#    path('AggUser/', listar_usuarios_registrar),
    path('AggUser/<int:pk>', views.AggUser, name='AggUser'),
    path('listUser/<int:pk>', views.UsersProyecto, name='UsersProyecto'),
    path('desvinculacionProyecto/<int:pk>/<int:pk_user>', views.desvinculacionProyecto, name='desvinculacionProyecto'),
    path('agregarUsuarios/<int:pk><int:nroFase>', views.agregarUsuarios, name='agregarUsuarios'),
    path('proyectos/', listar_proyectos, name='listar_proyectos'),
    path('cancelado/', proyectoCancelado, name='Proyectocancelado'),
    path('/itemCancelado/', itemCancelado, name='itemCancelado'),

    path('crear/TipoItem/<int:id_fase>',views.tipo_item_views_create,name='tipo_item_views_create'),
    path('crear/atributo/<str:nombre_ti>/<int:cantidad_atributos>/<int:fase_id>',views.add_atribute,name='add_atribute'),
    path('listar/usuarios/aprobados',views.ver_usuarios_aprobados,name='ver_usuarios_aprobados'),
    path('getUser/<int:pk>',views.get_user,name='get_user'),
    path('estadoProyecto/<int:pk>', views.estadoProyecto, name='estado_Proyecto'),
    path('detallesProyecto/<int:pk>', views.detallesProyecto, name='detalles_Proyecto'),
    path('verProyecto/<int:pk>', views.ver_proyecto, name='ver_proyecto'),
    path('ver/fase/<int:id_fase>/proyecto',views.get_fase_proyecto,name='get_fase_proyecto'),
    path('importar/tipo/item/fase/<int:id_fase>', views.importar_tipo_item, name='importar_tipo_item'),
    path('estadoProyecto/<int:pk>', views.estadoProyecto, name='estado_Proyecto'),
    path('enEspera/', VerUsersEnEspera.as_view(), name="listaDeEspera"),
    path('userEnEspera/<int:pk>', ActualizarUser.as_view(), name='userEsperando'),
    path('crearRol/<str:proyecto>', CrearRol.as_view(), name='crearRol'),
    path('modRol/<int:pk>', ModificarRol.as_view(), name='modificarRol'),
    path('lista/tipo/item/<int:id_proyecto>',views.listar_tipo_item, name='listar_tipo_item'),
    path('aggTI/<int:Fase>', views.agg_listar_tipo_item, name='agg_listar_tipo_item'),
    path('misRoles/<int:proyecto>', VerRoles.as_view(), name="misRoles"),
    path('crearItem/<int:Faseid>', views.crearItem, name="crearItem"),
    path('aggAtributos/<int:idTI>', views.aggAtributos, name="aggAtributos"),
    path('relacionarItem/<int:id_proyecto>/<int:id_item>', views.relacionarItem, name="relacionarItem"),
    path('detallesFase/<int:idFase>', views.detallesFase, name="detallesFase"),
    path('listar_relaciones/<int:idItem>', views.listar_relaciones, name="listar_relaciones"),
    path('listar_atributos/<int:idAtributoTI>/<int:id_item>', views.listar_atributos, name="listar_atributos"),
    path('comite/<int:pk>', views.comite, name='comite'),
    path('AggComite/<int:pk>', views.AggComite, name='AggComite'),
    path('desvinculacionComite/<int:pk>/<int:pk_user>', views.desvinculacionComite, name='desvinculacionComite'),

]


