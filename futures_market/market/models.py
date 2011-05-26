from django.db import models
from datetime import datetime

class Market(models.Model):
    question = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField('date created',default=datetime.now())
    cash_endowment = models.DecimalField(max_digits=8, decimal_places=2) # initial cash endowment for users, DLN is not sure what makes sense with this.
    # might be easier to make "cash" into a particular stock, with known fixed liquidation price == 1??
    market_open = models.BooleanField()

    def __unicode__(self):
        return self.question

class Stock(models.Model):
    market = models.ForeignKey(Market)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    # max liquidation_price $999999.99. this may be larger than necessary
    liquidation_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_shares = models.IntegerField() # number_users * endowment
    stock_endowment = models.IntegerField() # initial stock endowment for users
    
    last_sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    last_sale_time = models.DateTimeField('last sale time')

    def __unicode__(self):
        return self.name

class Trader(models.Model):
    market = models.ForeignKey(Market)
    name = models.CharField(max_length=20) # no particular reason
    
    cash = models.DecimalField(max_digits=8, decimal_places=2) # max_digits should be larger?

    def __unicode__(self):
        return self.name

class Holding(models.Model):
    market = models.ForeignKey(Market)
    stock = models.ForeignKey(Stock)
    trader = models.ForeignKey(Trader)
    
    shares = models.IntegerField()

    def __unicode__(self):
        return self.stock

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
    completion_time = models.DateTimeField(blank=True)

    def __unicode__(self):
        output = unicode(order) + ': ' + unicode(stock)
    
