from django.forms import ModelForm, ChoiceField, Form, FileField, ModelChoiceField, HiddenInput, ValidationError
from market.models import *

class OrderForm(ModelForm):
    """Order form used in trader view."""
    # from http://stackoverflow.com/questions/1697702/how-to-pass-initial-parameter-to-djangos-modelform-instance/1697770#1697770
    # price from http://stackoverflow.com/questions/6473895/how-to-restrict-values-in-a-django-decimalfield

    # restricts prices to 0.0 through 1.0
    PRICE_CHOICES = [(i*.01, str(i*.01)) for i in range(1,101)]
    price = ChoiceField(choices=PRICE_CHOICES)
    trader = ModelChoiceField(label='', queryset=Trader.objects.all(), widget=HiddenInput())
    market = ModelChoiceField(label='', queryset=Market.objects.all(), widget=HiddenInput())

    def clean(self):
        """Validates the data. Ensures the trader has enough cash or shares
           to complete the requested order."""

        cleaned_data = self.cleaned_data
        if cleaned_data.get('order') and cleaned_data.get('stock') \
            and cleaned_data.get('volume') and cleaned_data.get('price'):
                t = cleaned_data['trader']
                if cleaned_data['order'] == 'B': # buy order
                    open_orders = Order.objects.filter(trader=t,
                            order='B', completed=False)
                    open_order_value = float(sum([o.volume * o.price for o in open_orders]))
                    open_order_value += int(cleaned_data['volume']) * float(cleaned_data['price'])

                    if open_order_value > t.cash:
                        raise ValidationError("You don't have enough cash!")

                elif cleaned_data['order'] == 'S': # sell order!
                    open_orders = sum(Order.objects.filter(trader=t, order='S',
                            stock=cleaned_data['stock'],
                            completed=False).values_list('volume', flat=True))
                    open_orders += cleaned_data['volume']

                    if open_orders > t.holding_set.get(stock=cleaned_data['stock']).shares:
                        raise ValidationError("You don't have enough shares!")
        return cleaned_data

    class Meta:
        model = Order
        fields = ('stock', 'order', 'volume', 'price', 'trader', 'market')

class UploadFileForm(Form):
    file = FileField()
