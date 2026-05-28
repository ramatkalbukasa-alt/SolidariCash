from django import forms
from .models import Contribution

INPUT_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent'
SELECT_CLASS = 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer'


class ContributionPaymentForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['amount_paid', 'payment_method', 'payment_reference', 'payment_proof']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={
                'class': INPUT_CLASS, 'step': '0.01', 'min': '0',
                'placeholder': 'Montant payé'
            }),
            'payment_method': forms.Select(attrs={'class': SELECT_CLASS}),
            'payment_reference': forms.TextInput(attrs={
                'class': INPUT_CLASS, 'placeholder': 'Référence du paiement'
            }),
            'payment_proof': forms.FileInput(attrs={
                'class': 'w-full text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-green-600 file:text-white hover:file:bg-green-700 cursor-pointer'
            }),
        }


class ContributionValidateForm(forms.Form):
    DECISION_APPROVE = 'approve'
    DECISION_REJECT = 'reject'
    DECISION_LATE = 'late'
    DECISION_CHOICES = [
        (DECISION_APPROVE, 'Valider le paiement'),
        (DECISION_REJECT, 'Rejeter le paiement'),
        (DECISION_LATE, 'Marquer comme en retard'),
    ]

    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-green-500'})
    )
    admin_notes = forms.CharField(
        required=False, label='Notes admin',
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-slate-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none',
            'rows': 3, 'placeholder': 'Notes optionnelles...'
        })
    )
