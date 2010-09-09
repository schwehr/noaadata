#from django.db import models # Must use the next line for geodjango...
from django.contrib.gis.db import models

class Position(models.Model):
    key = models.IntegerField(primary_key=True)
    messageid = models.IntegerField()
    repeatindicator = models.IntegerField()
    userid = models.IntegerField()
    navigationstatus = models.IntegerField()
    rot = models.IntegerField()
    sog = models.DecimalField(max_digits=4, decimal_places=1)
    positionaccuracy = models.IntegerField()
    cog = models.DecimalField(max_digits=4, decimal_places=1)
    trueheading = models.IntegerField()
    timestamp = models.IntegerField()
    regionalreserved = models.IntegerField()
    spare = models.IntegerField()
    raim = models.BooleanField()
    state_syncstate = models.IntegerField()
    state_slottimeout = models.IntegerField()
    state_slotoffset = models.IntegerField()
    cg_r = models.CharField(max_length=15)
    cg_sec = models.IntegerField()
    cg_timestamp = models.DateTimeField()
    position = models.PointField(srid=4326)

    objects = models.GeoManager() # Required for geodjango

    def __str__(self):
        return str(self.userid) + ' ' + str(self.cg_timestamp)


    class Meta:
        db_table = u'position'

    # Enable admin interface
    class Admin:
        #pass
        list_display = ('userid','sog','cog','navigationstatus','position','cg_timestamp')
        list_filter = ('userid','sog','navigationstatus','cg_timestamp')
        search_fields = ('userid',)  # Broken?
        
class Shipdata(models.Model):
    key = models.IntegerField(primary_key=True)
    messageid = models.IntegerField()
    repeatindicator = models.IntegerField()
    userid = models.IntegerField()
    aisversion = models.IntegerField()
    imonumber = models.IntegerField()
    callsign = models.CharField(max_length=7)
    name = models.CharField(max_length=20)
    shipandcargo = models.IntegerField()
    dima = models.IntegerField()
    dimb = models.IntegerField()
    dimc = models.IntegerField()
    dimd = models.IntegerField()
    fixtype = models.IntegerField()
    etaminute = models.IntegerField()
    etahour = models.IntegerField()
    etaday = models.IntegerField()
    etamonth = models.IntegerField()
    draught = models.DecimalField(max_digits=3, decimal_places=1)
    destination = models.CharField(max_length=20)
    dte = models.IntegerField()
    spare = models.IntegerField()
    cg_r = models.CharField(max_length=15)
    cg_sec = models.IntegerField()
    cg_timestamp = models.DateTimeField()

    def __str__(self):
        return str(self.userid) + ' ' + self.name.strip('@') + ' ' + str(self.cg_timestamp)

    class Meta:
        db_table = u'shipdata'
    
    # Enable admin interface
    class Admin:
        #pass
        list_display = ('name','userid'
                        #,'imonumber'
                        #,'callsign'
                        ,'shipandcargo','draught','destination','cg_timestamp')
        list_filter = ('name','shipandcargo','draught','cg_timestamp')
        search_fields = ('name',)
