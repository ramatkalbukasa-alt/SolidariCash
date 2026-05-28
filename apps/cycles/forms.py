from django import forms
from .models import Cycle

INPUT_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-slate-500'
SELECT_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer'


class CycleForm(forms.ModelForm):
    class Meta:
        model = Cycle
        fields = ['name', 'description', 'start_date', 'end_date', 'contribution_amount', 'commission_rate']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ex: Cycle Janvier 2025'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none',
                'rows': 3, 'placeholder': 'Description optionnelle'
            }),
            'start_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'contribution_amount': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': '100.00', 'step': '0.01', 'min': '0'}),
            'commission_rate': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': '0.02', 'step': '0.001', 'min': '0', 'max': '1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end <= start:
            raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")
        return cleaned_data
