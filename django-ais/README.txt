My first try at a djano system for viewing what is in the AIS
database.  -kurt 2/2008

See: http://djangobook.com/

% mkdir django-ais && cd django-ais
% django-admin.py startproject ais_www
% cd ais_www

Edit settings.py to have these two lines:

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'ais'

% python manage.py inspectdb > foo.py

% python manage.py startapp msgs

Edit msgs/models.py with output from foo.py

Edit settings.py to have this:

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.sites',
    'ais_www.msgs'
)

% python manage.py validate
