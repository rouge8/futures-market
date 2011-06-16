from django.db import models
from market import Market
from stock import Stock
from trader import Trader
from datetime import datetime

class Order(models.Model):
    market = models.ForeignKey(Market)
    stock = models.ForeignKey(Stock)
    trader = models.ForeignKey(Trader)
    
    ORDER_CHOICES = (
            ('B', 'Buy'),
            ('S', 'Sell'),
        )
    order = models.CharField(max_length=1, choices=ORDER_CHOICES)
    creation_time = models.DateTimeField(default=datetime.now())
    volume = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    completed = models.BooleanField()
    completion_time = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        ### MAKE THIS BETTER
        return unicode(self.order) + ': ' + unicode(self.stock.name)

    class Meta:
        app_label = 'market'
