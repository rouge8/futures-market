from django.db import models
from market import Market

class Stock(models.Model):
    market = models.ForeignKey(Market)
    name = models.CharField(max_length=500)
    # max liquidation_price $999999.99. this may be larger than necessary
    liquidation_price = models.DecimalField(max_digits=8, decimal_places=2)
    stock_endowment = models.IntegerField() # initial stock endowment for users
    
    last_sale_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    last_sale_time = models.DateTimeField('last sale time', null=True, blank=True)

    class Meta:
        unique_together = ('market', 'name')
        app_label = 'market'

    def __unicode__(self):
        return self.name
