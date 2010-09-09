from django.conf.urls.defaults import *

urlpatterns = patterns(''
    ,(r'^admin/', include('django.contrib.admin.urls'))
    # Example:
    # (r'^ais/', include('ais.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
