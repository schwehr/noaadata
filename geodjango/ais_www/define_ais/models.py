from django.db import models


class Dac(models.Model):
    country = models.CharField(max_length=60)
    code = models.PositiveIntegerField()

    def __str__(self):
        return str(self.code) + ' - ' + self.country

    class Admin:
        list_display = ('country','code')
        ordering = ( 'code', )
#        pass

class Type(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Admin:
        pass


class Unit(models.Model):
    name = models.CharField(max_length=10)
    shortdescription = models.CharField(max_length=30)
    description = models.TextField()
    refURL = models.URLField()
    def __str__(self):
        name = self.name
        if len(name)==0: name = 'None'
        return name + ' - ' + self.shortdescription

    class Admin:
        pass


class Aismsg(models.Model):
    name = models.CharField(max_length=20,help_text='SQL compatible name [a-zA-Z][a-zA-Z0-9_]*')
    msgnum = models.PositiveIntegerField(help_text='6 for address; 8 for broadcast; or ...')
    #dac = models.PositiveIntegerField(help_text='Country code')
    dac = models.ForeignKey(Dac,help_text='Country code')
    fi = models.PositiveIntegerField(help_text='Functional Identifier number in 1..63 for a particular DAC')
    description = models.TextField(help_text='First sentence should be stand alone, short description.  Then detailed field description')

    # Recommendations
    #transmit_rec = models.XMLField(help_text='Description of how frequent to transmit and when to drop from the queue.  How long to archive..  How long to fall off the earth')
    transmit_rec = models.TextField(help_text='Description of how frequent to transmit and when to drop from the queue.  How long to archive..  How long to fall off the earth')
    #display_rec = models.XMLField(help_text='Similiar to S100.  How to display')

    #receive_rec How to handle received messages.  Drop, keep, update, timeout etc.

    display_rec = models.TextField(help_text='Similiar to S100.  How to display')

    note = models.TextField(help_text='Additional notes that are not as important as the description')
    
    

    def __str__(self):
        return self.name + ' ('+str(self.dac)+':'+str(self.fi)+')'
        #return self.name + ' ( FIX: dac:'+str(self.fi)+')'

    class Admin:
        pass

class Field(models.Model):
    aismsg = models.ForeignKey(Aismsg)
    order = models.PositiveIntegerField(help_text='Where in the message should this field sit?')
    name = models.CharField(max_length=20,help_text='SQL/XML compatible name.  [a-zA-Z][a-zA-Z0-9_]*')
    description = models.TextField(help_text='First line should stand alone')
    numberofbits = models.PositiveIntegerField(help_text='total number of bits or if an array it is the size of each element (e.g. 6 for aisstr6)')
    arraylength = models.PositiveIntegerField(help_text='Number of elements (e.g. string length for an aisstr6)')
    type = models.ManyToManyField(Type,help_text='Type of each element')
    unavailable = models.CharField(max_length=120,help_text='Value to use if the field value is unknown or unavailable')
    units = models.ForeignKey(Unit,help_text='Remember that the display system can localize units')
    
    #note = models.TextField(help_text='Additional notes that are not as important as the description')

    #decimal_places = models.PositiveIntField(null=True,help_text='How many decimal places.  Leave blank if necessary')

    # decimalplaces
    # scale
    # range min and range max
    # note

    def __str__(self):
        s = str(self.aismsg.dac.code) 
        s += ':' + str(self.aismsg.fi)
        s += ' ' + str(self.aismsg.name) 
        s += ' - ' 
        s += self.name 
        return s

    class Admin:
        pass


