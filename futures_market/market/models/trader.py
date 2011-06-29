from django.db import models
from market import Market

class Trader(models.Model):
    market = models.ForeignKey(Market)
    name = models.CharField(max_length=20) # no particular reason
    
    cash = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('market', 'name')
        app_label = 'market'

    def __unicode__(self):
        return self.name
