from django.forms import ModelForm, ChoiceField
from market.models import *

class OrderForm(ModelForm):
    # from http://stackoverflow.com/questions/1697702/how-to-pass-initial-parameter-to-djangos-modelform-instance/1697770#1697770
    # price from http://stackoverflow.com/questions/6473895/how-to-restrict-values-in-a-django-decimalfield

    PRICE_CHOICES = [(i*.01, str(i*.01)) for i in range(1,101)]
    price = ChoiceField(choices=PRICE_CHOICES)

    class Meta:
        model = Order
        fields = ('stock', 'order', 'volume', 'price')
