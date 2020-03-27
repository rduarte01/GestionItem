from django import forms
from django.forms import Textarea
from .models import Fase
from django.contrib.auth.models import User, Permission,Group
from .models import Proyecto,TipoItem,Atributo
####### se escribe formulario
from django.forms.widgets import SelectMultiple, CheckboxSelectMultiple

class FormUserAgg(forms.ModelForm):
    class Meta:
        model = User
        fields=['username']
        permissions =forms.ModelMultipleChoiceField(
            queryset = Permission.objects.all(),
            required= False,
        )


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
                "users",
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



class TipoItemForm(forms.ModelForm):
    """
        En esta clase se define la estrutura del formulario para crear un tipo de item
    """
    class Meta:
        model=TipoItem
        fields=['nombre']
        labels={
            'nombre': 'Nombre del Tipo de Item'
        }
        widgets={
            'nombre':forms.TextInput(
                attrs={
                    'placeholder':"Nombre del Tipo de Item",
                    'class':"form-control"
                }
            )
        }
    cantidad=forms.IntegerField(label="Cantidad de Atributos del Tipo de Item",
                                max_value=10,required=True,
                                widget=forms.TextInput(
                                        attrs={
                                            "placeholder": "Cantidad Tipo Item",
                                            'class':"form-control"
                                            }
                                        )
                                )

class FaseForm(forms.ModelForm):
    """
    HACE REFERENCIA AL MODELO FASE QUE SERA REPRESENTADO POR MEDIO DE ESTA CLASE FORMLARIO EN EL NAVEGADOR WEB
    CON SUS RESPECTIVOS CAMPOS A COMPLETAR
    """
    class Meta:
        model = Fase
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
    Consulta = forms.CharField(widget=forms.Textarea)

class AtributeForm(forms.ModelForm):
    class Meta:
        model=Atributo
        fields=('nombre','es_obligatorio','tipo_dato')
        labels={
            'nombre':'Nombre del atributo',
            'es_obligatorio':'Obligatoriedad del Tipo de Item',
            'tipo_dato':'Tipo de dato del atributo'
        }
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
    def __init__(self, *arg, **kwarg):
        super(AtributeForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = True


class SettingsUserFormJesus(forms.Form):
    is_admin=forms.BooleanField(
                                required=False,
                                label="ES ADMINISTRADOR",
                                )
    is_manager=forms.BooleanField(required=False,label="ES Gerenete Proyecto")
    State_CHOICES = [
        ('True', 'Aprobado'),
        ('False', 'Desactivado'),
    ]
    estado=forms.ChoiceField(
        label="Estado del Usuario",
        required=True,
        widget=forms.Select(attrs={"class":"form-control" }),
        choices=State_CHOICES,
    )

class SettingsUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','esta_aprobado']
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electronico del Usuario',
            'esta_aprobado': 'Estado del usuario',
        }
        OPTIONS = (
            ('True', "Aprobado"),
            ('False', "En Espera"),
        )
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre de usuario',
                    'id': 'username'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Correo Electronico del Usuario',
                    'id': 'email'
                }
            ),
            'esta_aprobado': forms.RadioSelect(choices=[
                (True, 'Activo'),
                (False, 'En Espera')
            ]),
        }


class RolForm(forms.ModelForm):
    class Meta:

        model = Group
        fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


            for perm in self.permissions:
                self.fields[perm].widget.attrs['class'] = 'form-control'


        widgets={
            'name':forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Ingrese nombre del Rol',
                }
            ),
            'permissions':forms.CheckboxSelectMultiple(),
        }

