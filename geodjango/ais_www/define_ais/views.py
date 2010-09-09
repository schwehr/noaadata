# Create your views here.

from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response


def msgtoc(request):
    html = "<html><body>Table of contentsurlpattern for test works %s</body></html>"
    return HttpResponse(html)


def msg(request,msgid):
    html = "<html><body>urlpattern for test works %s</body></html>" % msgid
    return HttpResponse(html)
