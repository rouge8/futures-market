from django.db import models
from datetime import datetime

class Market(models.Model):
    question = models.CharField(max_length=500, unique=True)
    description = models.TextField(blank=True)
    slug = models.CharField(max_length=100, unique=True)
    creation_date = models.DateTimeField('date created',default=datetime.now())
    cash_endowment = models.DecimalField(max_digits=8, decimal_places=2) # initial cash endowment for users, DLN is not sure what makes sense with this.
    # might be easier to make "cash" into a particular stock, with known fixed liquidation price == 1??
    market_open = models.BooleanField()
    
    class Meta:
        unique_together=('question',)
        app_label = 'market'

    def __unicode__(self):
        return self.question
