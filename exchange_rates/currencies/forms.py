from django import forms


class CurrencyForm(forms.Form):
    currency_pairs = forms.MultipleChoiceField(
        choices=[
            ('USD/PLN', 'USD/PLN'),
            ('EUR/PLN', 'EUR/PLN'),
            ('CHF/PLN', 'CHF/PLN'),
            ('CHF/USD', 'CHF/USD'),
            ('EUR/USD', 'EUR/USD')
        ],
        widget=forms.CheckboxSelectMultiple,
        label='Which exchange rate information do you want to see?'
    )
