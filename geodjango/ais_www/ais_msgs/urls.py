from django.conf.urls.defaults import *



urlpatterns = patterns('ais_www.ais_msgs.views',
                       (r'^test$','test'),
                       (r'^$','directory'),
                       (r'^position/$','position'),
                       #(r'^position/mmsi/(?P<userid>d+)/$','position_by_userid'),
                      )
