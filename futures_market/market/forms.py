from django.forms import ModelForm
from market.models import *

class OrderForm(ModelForm):
    # from http://stackoverflow.com/questions/1697702/how-to-pass-initial-parameter-to-djangos-modelform-instance/1697770#1697770

    class Meta:
        model = Order
        fields = ('stock', 'order', 'volume', 'price')
