# Create your views here.

from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context

from django.shortcuts import render_to_response

import datetime

import ais_msgs.models
from ais_msgs import models

def test(request):
    html = "<html><body>urlpattern for test works</body></html>"
    return HttpResponse(html)

def directory(request):
    ''' FIX: this should be dynamically generated '''
    l = ['<html><body>',]
    # This in not a template with a context... oops
    #l.append ('Welcome {{ user }}')
    l.append ('Available message pages:<ul>')
    # FIX: get pages from some master list, or scrap from the xml?
    pages=['position','bsreport','shipdata']
    for page in pages:
        l.append('  <li><a href="'+page+'/">'+page+'</a></li>')
    l.append('</ul></body></html>')
    return HttpResponse('\n'.join(l))

def position(request):
    now = datetime.datetime.now()
    #t = get_template('position.html')
    vessels = ais_msgs.models.Position.objects.all()[:20]
    #print len(vessels)
    return render_to_response('position.html',{'vessels':vessels,'current_date':now})
    #return HttpResponse(t.render(Context({'current_date':now}) ) )

#def position_userid(request,userid):
#    now = datetime.datetime.now()
    #vessels = ais_msgs.models.Position.objects.all()[:10]
#    try:
#        vessels = ais_msgs.models.Position.objects.filter(userid=userid)[:10]
#    except ais_msgs.models.Position.DoesNotExit:
#        raise Http404

#    return list_detail.object_list(
#        request,
#        queryset = models.Position.objects.filter(userid=userid)[:10]
#        template_name
# P 130...
    #print len(vessels),userid
    
    #return render_to_response('position.html',{'vessels':vessels,'current_date':now})
    
