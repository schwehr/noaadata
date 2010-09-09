from django.conf.urls.defaults import *

import ais_www.define_ais.views

#urlpatterns = patterns('',
#                       ('^msg/(?P<msgid>\d/$','ais_www.define_ais.views.msg'),
#)

#urlpatterns += patterns('',
#                
#                        )

urlpatterns = patterns('',
                       ('^msg/$',ais_www.define_ais.views.msgtoc)
                       ,('^msg/(?P<msgid>\d)/$',ais_www.define_ais.views.msg)
)
