from django import forms
from django.contrib.auth import get_user_model
from .models import Member, Head

User = get_user_model()

INPUT_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-slate-500'
SELECT_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer'
TEXTAREA_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none'


class MemberCreateForm(forms.Form):
    username = forms.CharField(
        max_length=150, label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': "Nom d'utilisateur"})
    )
    first_name = forms.CharField(
        max_length=150, label='Prénom',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        max_length=150, label='Nom',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nom de famille'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'email@exemple.com'})
    )
    phone = forms.CharField(
        max_length=20, label='Téléphone', required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+xxx xxx xxx xxx'})
    )
    address = forms.CharField(
        label='Adresse', required=False,
        widget=forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'Adresse complète'})
    )
    national_id = forms.CharField(
        max_length=50, label='Numéro national', required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Numéro de pièce d\'identité'})
    )
    head_count = forms.IntegerField(
        min_value=1, max_value=10, initial=1, label='Nombre de têtes',
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': '1', 'min': 1, 'max': 10})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Mot de passe'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email


class MemberUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150, label='Prénom',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    last_name = forms.CharField(
        max_length=150, label='Nom',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': INPUT_CLASS})
    )
    phone = forms.CharField(
        max_length=20, required=False, label='Téléphone',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )

    class Meta:
        model = Member
        fields = ['national_id', 'emergency_contact', 'emergency_phone', 'notes']
        widgets = {
            'national_id': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'emergency_contact': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'emergency_phone': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
        }


class HeadAddForm(forms.Form):
    count = forms.IntegerField(
        min_value=1, max_value=10, label='Nombre de têtes à ajouter',
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': '1', 'min': 1, 'max': 10})
    )


class SuspendMemberForm(forms.Form):
    reason = forms.CharField(
        label='Motif de suspension',
        widget=forms.Textarea(attrs={
            'class': TEXTAREA_CLASS,
            'rows': 4,
            'placeholder': 'Expliquez le motif de la suspension...'
        })
    )
