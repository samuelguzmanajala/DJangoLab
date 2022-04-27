"""
Definition of forms.
"""

from django import forms
from app.models import Pelicula
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class RegistroForm(forms.Form): #Manualko erregistratzeko formularioa
    username = forms.CharField(max_length=100) #Nombre
    pass1 = forms.CharField(widget=forms.PasswordInput) #Lehen pasahitza
    pass2 = forms.CharField(widget=forms.PasswordInput) #Errepikatutako pasahitza

class PeliculaForm(forms.ModelForm):
        class Meta:
            model = Pelicula
            fields = ('titulo','direccion','anio','genero','sinopsis','votos')