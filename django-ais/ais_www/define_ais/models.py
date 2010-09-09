from django.db import models


class Dac(models.Model):
    country = models.CharField(maxlength=60)
    code = models.PositiveIntegerField()

    def __str__(self):
        return str(self.code) + ' - ' + self.name

    class Admin:
        pass

class Type(models.Model):
    name = models.CharField(maxlength=20)

    def __str__(self):
        return self.name

    class Admin:
        pass


class Unit(models.Model):
    name = models.CharField(maxlength=10)
    shortdescription = models.CharField(maxlength=30)
    description = models.TextField()
    refURL = models.URLField()
    def __str__(self):
        name = self.name
        if len(name)==0: name = 'None'
        return name + ' - ' + self.shortdescription

    class Admin:
        pass


class Aismsg(models.Model):
    name = models.CharField(maxlength=20)
    description = models.TextField()
    msgnum = models.PositiveIntegerField()
    dac = models.PositiveIntegerField()
    fi = models.PositiveIntegerField()

    def __str__(self):
        return self.name + ' ('+str(self.dac)+':'+str(self.fi)+')'

    class Admin:
        pass

class Field(models.Model):
    aismsg = models.ForeignKey(Aismsg)
    name = models.CharField(maxlength=20)
    description = models.TextField()
    numberofbits = models.PositiveIntegerField()
    type = models.ManyToManyField(Type)
    unavailable = models.CharField(maxlength=120)
    units = models.ForeignKey(Unit)
    
    # decimalplaces
    # scale
    # range min and range max
    # note

    class Admin:
        pass


