from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-slate-500',
            'placeholder': "Nom d'utilisateur",
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-slate-500',
            'placeholder': 'Mot de passe',
        })
    )


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_class = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent'
        for field in self.fields.values():
            field.widget.attrs['class'] = field_class


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_class = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent'
        for field in self.fields.values():
            field.widget.attrs['class'] = field_class


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500',
            'placeholder': 'Ancien mot de passe',
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500',
            'placeholder': 'Nouveau mot de passe',
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500',
            'placeholder': 'Confirmer le nouveau mot de passe',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data
