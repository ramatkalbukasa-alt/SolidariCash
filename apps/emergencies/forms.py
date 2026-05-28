from django import forms
from .models import Emergency

INPUT_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent'
TEXTAREA_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none'


class EmergencySubmitForm(forms.ModelForm):
    class Meta:
        model = Emergency
        fields = ['head', 'reason', 'justification_document']
        widgets = {
            'head': forms.Select(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer'
            }),
            'reason': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS, 'rows': 5,
                'placeholder': 'Décrivez votre urgence en détail...'
            }),
            'justification_document': forms.FileInput(attrs={
                'class': 'w-full text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-green-600 file:text-white hover:file:bg-green-700 cursor-pointer'
            }),
        }


class EmergencyDecisionForm(forms.Form):
    DECISION_APPROVE = 'approve'
    DECISION_REFUSE = 'refuse'
    DECISION_CHOICES = [
        (DECISION_APPROVE, 'Approuver'),
        (DECISION_REFUSE, 'Refuser'),
    ]

    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-green-500'})
    )
    new_position = forms.IntegerField(
        required=False, min_value=1, label='Nouvelle position (si approuvée)',
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS, 'placeholder': 'Nouvelle position dans la rotation', 'min': 1
        })
    )
    decision_notes = forms.CharField(
        required=False, label='Notes de décision',
        widget=forms.Textarea(attrs={
            'class': TEXTAREA_CLASS, 'rows': 3,
            'placeholder': 'Motif de la décision...'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        decision = cleaned_data.get('decision')
        new_position = cleaned_data.get('new_position')
        if decision == self.DECISION_APPROVE and not new_position:
            raise forms.ValidationError("Veuillez indiquer la nouvelle position pour l'urgence approuvée.")
        return cleaned_data
