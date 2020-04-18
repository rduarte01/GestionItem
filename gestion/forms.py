from django import forms
from django.forms import Textarea
from .models import Fase
from django.contrib.auth.models import User, Permission,Group,ContentType
from .models import Proyecto,TipoItem,Atributo,Usuario,Item,Atributo_Item
####### se escribe formulario
from django.forms.widgets import SelectMultiple, CheckboxSelectMultiple




class FormItem(forms.ModelForm):
    """
    """

    class Meta:
        """META PARA DEFINIR LOS CAMPOS A MOSTRAR EN EL FORMULARIO"""
        model = Item
        """SE REALIZA FORMULARIO DEL MODELO PROYECTO"""
        fields = [
                "nombre",
                "descripcion",
                "costo",
                  ]
        """CAMPOS A MOSTRAR EN EL FORMULARIO"""
        labels= {
            "nombre":"Ingrese un Nombre para el Item",
            "descripcion":"Ingrese una descripcion si lo desea",
            "costo":"Costo",
        }
        """LA ETIQUETA DE CADA CAMPO"""
        widgets={
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "costo": forms.TextInput(attrs={'class': 'form-control'}),
        }
        """LOS WIDGETS PARA CADA CAMPO AJUSTANDO A LO QUE SE NECESITA"""



class FormProyectoEstados(forms.Form):
    """FORM PARA MOSTRAR LOS ESTADOS QUE PUEDE TENER UN PROYECTO"""
    State_CHOICES = [
        ("INICIADO", "INICIADO"),
        ("FINALIZADO", "FINALIZADO"),
        ("CANCELADO", "CANCELADO")
    ]
    """MEDIANTE CHOICES MOSTRAMOS LAS OPCIONES EN EL HTML"""

    estado = forms.ChoiceField(
        label="Estado del Proyecto",
        required="Creado",
        widget=forms.Select(attrs={"class":"form-control" }),
        choices=State_CHOICES,
    )
    """EL ESTADO CON EL CUAL GUARDAREMOS EL POST"""

class FormProyecto(forms.ModelForm):
    """
    FORMULARIO PARA INICIO DE PROYECTO EN DONDE SE MOSTRARN LOS CAMPOS COMO NOMBRE DE PROYECTO,
    DESCRIPCION, ESTADO Y SE DESPLEGARAN LOS USUARIOS A SER AÑADIDOS AL PROYECTO EN CREACION
    """
    fase = forms.IntegerField()
    class Meta:
        """META PARA DEFINIR LOS CAMPOS A MOSTRAR EN EL FORMULARIO"""
        model = Proyecto
        """SE REALIZA FORMULARIO DEL MODELO PROYECTO"""
        fields = [
                "nombre",
                "descripcion",

                  ]
        """CAMPOS A MOSTRAR EN EL FORMULARIO"""
        labels= {
            "nombre":"Ingrese un Nombre para el proyecto",
            "descripcion":"Ingrese una descripcion si lo desea",
            "users":"Seleccione los usuarios a añadir",
        }
        """LA ETIQUETA DE CADA CAMPO"""
        widgets={
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "users": forms.CheckboxSelectMultiple(),
        }
        """LOS WIDGETS PARA CADA CAMPO AJUSTANDO A LO QUE SE NECESITA"""


#jesus
class TipoItemForm(forms.ModelForm):
    """
        En esta clase se define la estrutura del formulario para crear un tipo de item
    """
    class Meta:
        ''' Clase que se utiliza para proveer metadatos al form AtrributeForm'''
        model=TipoItem
        ''' atributo que especifica a que modelo esta relacionado este form'''
        fields=['nombre']
        '''atributos que vamos a desplegar en nuestro form'''
        labels={
            'nombre': 'Nombre del Tipo de Item'
        }
        '''los labels que se mostraran para cada fields en nuestro html'''
        widgets={
            'nombre':forms.TextInput(
                attrs={
                    'placeholder':"Nombre del Tipo de Item",
                    'class':"form-control"
                }
            )
        }
        '''widget para especificar las clase de bootstap utilizada en nuestro html para nuestro form'''
    cantidad=forms.IntegerField(label="Cantidad de Atributos del Tipo de Item",
                                max_value=10,required=False,
                                widget=forms.TextInput(
                                        attrs={
                                            "placeholder": "Cantidad Tipo Item",
                                            'class':"form-control"
                                            }
                                        )
                                )
    '''este atributo se utiliza para obetener la cantidad de atributos que va a tener el tipo de item '''

class FaseForm(forms.ModelForm):
    """
    HACE REFERENCIA AL MODELO FASE QUE SERA REPRESENTADO POR MEDIO DE ESTA CLASE FORMLARIO EN EL NAVEGADOR WEB
    CON SUS RESPECTIVOS CAMPOS A COMPLETAR
    """
    class Meta:
        """METADATOS PARA FORM FASE"""
        model = Fase
        """UTILIZA EL MODELO FASE"""
        fields = [#'id_Fase',
                  'nombre',
                  'descripcion'
        ]
        """CAMPOS A SER COMPLETADOS EN EL FORMULARIO WEB A PRESENTAR"""

        labels = {
        #"id_Fase": "N° Fase",
        "nombre": "Nombre",
        "descripcion": "Descripción",
        #"estado": "Estado",
        #"id_Proyecto": "ID_Proyecto",
        }

        widgets = {
        #"id_Fase": forms.IntegerField(),
        "nombre" : forms.TextInput(attrs = {'class': 'form-control'}),
        "descripcion": forms.TextInput(attrs = {'class': 'form-control'}),
        #"estado": forms.TextInput(attrs = {'class': 'form-control'}),
        }

class FormAyuda(forms.Form):
    """FORM PARA GUARDAR LA CONSULTA DEL USUARIO"""
    Consulta = forms.CharField(widget=forms.Textarea)
    """PARA CAPTURAR EL MENSAJE Y RECIBIR EN EL POST"""


#jesus
class AtributeForm(forms.ModelForm):
    '''
        Este es el form que se va a utilizar en un HTML a la hora de crear un atributo para un tipo de Item
    '''
    class Meta:
        ''' Clase que se utiliza para proveer metadatos al form AtrributeForm'''
        model=Atributo
        ''' atributo que especifica a que modelo esta relacionado este form'''
        fields=('nombre','es_obligatorio','tipo_dato')
        '''atributos que vamos a desplegar en nuestro form'''
        labels={
            'nombre':'Nombre del atributo',
            'es_obligatorio':'Obligatoriedad del Tipo de Item',
            'tipo_dato':'Tipo de dato del atributo'
        }
        '''los labels que se mostraran para cada fields en nuestro html'''
        widgets={
            'nombre': forms.TextInput(
                attrs={
                    'placeholder': "Nombre del Atributo",
                    'class': "form-control"
                }
            ),
            'es_obligatorio': forms.CheckboxInput(
                attrs={
                    'class':'form-check-input'
                }
            ),
            'tipo_dato':forms.Select(
                attrs={
                    'class':'form-control'
                }
            )
        }
        '''widget para especificar las clase de bootstap utilizada en nuestro html para nuestro form'''
    def __init__(self, *arg, **kwarg):
        super(AtributeForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = True

#jesus
class SettingsUserFormJesus(forms.Form):
    '''
        Este es el form que se va a utilizar en un HTML para settear los permisos y los estados de los usuarios
    '''
    is_admin=forms.BooleanField(
                                required=False,
                                label="Es Administrador",
                                )
    '''variable boolean para settear si el usuario tendra el permiso es_administrador '''
    is_manager=forms.BooleanField(required=False,label="Es Gerente Proyecto")
    '''variable boolean para settear si el usuario tendra el permiso es_gerente_proyecto '''
    State_CHOICES = [
        ('True', 'Aprobado'),
        ('False', 'Desactivado'),
    ]
    '''estan son las opciones que el usuario tedra podra seleccionar en el estado del usuario  '''
    estado=forms.ChoiceField(
        label="Estado del Usuario",
        required=True,
        widget=forms.Select(attrs={"class":"form-control" }),
        choices=State_CHOICES,
    )
    '''variable que se utilizara para settear el estado del usuario atravez de un select '''

#GER
class PerfilUserEnEspera(forms.ModelForm):
    """Muestra el perfil del Usuario a Que esta en
    espera de ser aprobado dentro del sistema, se le pasan
    los datos del username, email, estado, y la fecha de registro, el unico
    dato que el administrador podra modificar obviamente sera el estado
    en que se encuentra el usuario"""

    class Meta:
        model = Usuario
        fields = ['esta_aprobado']
        labels = {
            'esta_aprobado': 'Estado del usuario',
        }
        widgets = {
            'esta_aprobado': forms.RadioSelect(choices=[
                (True, 'Activo'),
                (False, 'En Espera')
            ]),
        }

class RolForm(forms.ModelForm):
    """Form destinado para la creacion de un Rol especifico
    dentro de un proyecto, se filtran los permisos  por el 'content_type=19',
    que es el modelo donde se encuentran todos los permisos que se pueden asignar
    a un proyecto"""
    def __init__(self, *args,**kwargs):
        super(RolForm,self).__init__(*args,**kwargs)
        content_type=ContentType.objects.get(model='permisos')
        self.fields['permissions'].queryset = Permission.objects.filter(content_type=content_type.id)
    class Meta:
        model = Group
        fields = "__all__"
        widgets={
            'name':forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Ingrese nombre del Rol',
                }
            ),
            'permissions':forms.CheckboxSelectMultiple(),
        }


