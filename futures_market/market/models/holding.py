from django.db import models
from market import Market
from stock import Stock
from trader import Trader

class Holding(models.Model):
    """Represents a holding in the market. Must be unique for the combination
       of (market, stock, trader)."""
    market = models.ForeignKey(Market)
    stock = models.ForeignKey(Stock)
    trader = models.ForeignKey(Trader)
    
    shares = models.IntegerField()

    class Meta:
        unique_together = ('market', 'stock', 'trader')
        app_label = 'market'

    def __unicode__(self):
        output = unicode(self.trader) + ': ' + unicode(self.stock) + ' ' + unicode(self.shares)
        return output
