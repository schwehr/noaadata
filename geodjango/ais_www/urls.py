from django.conf.urls.defaults import *
from hello import current_datetime
#import hello_template.current_datetime
from hello_template import current_datetime as current_datetime_template
import hello_template
import ais_msgs.views

# Setup databrowse module
from django.contrib import databrowse
import ais_www.ais_msgs as ais_msgs
import ais_www.define_ais as define_ais
#import Position,Shipdata

databrowse.site.register(ais_msgs.models.Position)
databrowse.site.register(ais_msgs.models.Shipdata)
databrowse.site.register(define_ais.models.Aismsg)
databrowse.site.register(define_ais.models.Field)
#databrowse.site.register()


urlpatterns = patterns('',
                       (r'^time/$',current_datetime),
                       (r'^time/template/$',hello_template.current_datetime),
                       (r'^admin/', include('django.contrib.admin.urls')),
                       (r'^define_ais/', include('ais_www.define_ais.urls'))
                       #(r'^position/$', ais_msgs.views.position),
                       #(r'^position/mmsi/(?P<userid>\d{9})/$', 'ais_msgs.views.position_userid'),
#                       (r'^msgs/',include('ais_www.ais_msgs.urls')),
)

urlpatterns += patterns('',
                        (r'^msgs/',include('ais_www.ais_msgs.urls')),
                        )

urlpatterns += patterns ('',
                        (r'^databrowse/(.*)', databrowse.site.root),
                        )
