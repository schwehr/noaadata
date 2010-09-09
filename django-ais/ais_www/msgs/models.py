from django.db import models

# Create your models here.

class Position(models.Model):
    key = models.IntegerField(primary_key=True)
    messageid = models.IntegerField()
    repeatindicator = models.IntegerField()
    userid = models.IntegerField()
    navigationstatus = models.IntegerField()
    rot = models.IntegerField()
    sog = models.FloatField(max_digits=4, decimal_places=1)
    positionaccuracy = models.IntegerField()
    cog = models.FloatField(max_digits=4, decimal_places=1)
    trueheading = models.IntegerField()
    timestamp = models.IntegerField()
    regionalreserved = models.IntegerField()
    spare = models.IntegerField()
    raim = models.BooleanField()
    state_syncstate = models.IntegerField()
    state_slottimeout = models.IntegerField()
    state_slotoffset = models.IntegerField()
    cg_r = models.CharField(maxlength=15)
    cg_sec = models.IntegerField()
    cg_timestamp = models.DateTimeField()
    position = models.TextField() # This field type is a guess.
    class Meta:
        db_table = 'position'

    def __str__(self):
        return self.userid

class TrackLines(models.Model):
    ogc_fid = models.IntegerField(primary_key=True)
    userid = models.IntegerField()
    name = models.CharField(maxlength=20)
    track = models.TextField() # This field type is a guess.
    class Meta:
        db_table = 'track_lines'
        ordering = ['userid']
    def __str__(self):
        return '%s track line' % self.name

class LastPosition(models.Model):
    key = models.IntegerField(primary_key=True) 
    userid = models.IntegerField()
    name = models.CharField(maxlength=20)
    cog = models.IntegerField()
    sog = models.TextField() # This field type is a guess.
    cg_timestamp = models.DateTimeField()
    position = models.TextField() # This field type is a guess.
    class Meta:
        ordering = ['cg_timestamp'] # Doesn't seem to like the - here for reverse
        db_table = 'last_position'

    def __str__(self):
        return '%s last position' % self.name

    # Enable the admin interface
    class Admin:
        list_display = ('userid','name','cog','cg_timestamp')
        #ordering = ('-cg_timestamp')
