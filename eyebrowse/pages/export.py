
# 
from eyebrowse.models import *
import csv
import StringIO,zipfile
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse,HttpResponseRedirect, HttpResponseForbidden
from django.http import Http404

import random
seed = repr(random.random())

def h(s):
    import md5
    md5 = md5.md5()
    md5.update(s + seed)
    return md5.hexdigest()

identity = lambda s: s

def get_cols(obfuscator=h):
    return {
        'username': lambda pageview: obfuscator(pageview.user.email),
        'start_time': lambda pageview: pageview.startTime,
        'end_time': lambda pageview: pageview.endTime,
        'url': lambda pageview: pageview.url,
        'host': lambda pageview: pageview.host
    }     

def dump_file(filename='/tmp/foo.csv',user=None,pvrecords=None):
    f = open(filename,'w')    
    csv_writer = csv.writer(f, dialect='excel')
    if user:
        pvrecords = PageView.objects.filter(user=user).order_by('startTime')
        colgens = get_cols(identity) # no encryption
        csv_writer.writerow(colgens.keys())
        for x in pvrecords:
            csv_writer.writerow([ col(x) for col in colgens.values() ])
    else:
        pvrecords = PageView.objects.all().order_by('startTime')
        colgens = get_cols(h) # no encryption
        csv_writer.writerow(colgens.keys())
        for x in pvrecords:
            csv_writer.writerow([col(x) for col in colgens.values() ])
    f.close()

def get_dupes():
    pviews = PageView.objects.all()
    views = {}
    dupes = []
    sig = lambda pv: "%s-%s-%s" % (repr(pv.startTime),repr(pv.url),repr(pv.user.id))
    for pv in pviews:
        spv = sig(pv)
        if not spv in views:
            views[spv] = True
            continue
        dupes.append(pv.id)
    return dupes

def dump_pageviews_csv(fle,user=None):
    csv_writer = csv.writer(fle, dialect='excel')
    if user:
        pvrecords = PageView.objects.filter(user=user).order_by('startTime')
        colgens = get_cols(identity) # no encryption
        csv_writer.writerow(colgens.keys())
        for x in pvrecords:
            csv_writer.writerow([ col(x) for col in colgens.values() ])
    else:
        pvrecords = PageView.objects.all().order_by('startTime')
        colgens = get_cols(h) # no encryption
        csv_writer.writerow(colgens.keys())
        for x in pvrecords:
            csv_writer.writerow([col(x) for col in colgens.values() ])

def _dump_pageviews_to_sio(u=None,filesuffix='database'):
    ## creates a sio object to dump things to
    sio = StringIO.StringIO()
    dump_pageviews_csv(sio,u)
    zio = StringIO.StringIO()
    zf = zipfile.ZipFile(zio,mode='a')
    zf.writestr('eyebrowse-%s.csv' % filesuffix,sio.getvalue())
    zf.close()
    return zio
            
def get_user_pageviews_as_csv_view(request):
    ## get user from request (brenn)
    u = get_object_or_404(User, username=request.user.username)
    zio = _dump_pageviews_to_sio(u,u.username)
    response = HttpResponse(content_type='application/x-zip-compressed')
    response.write(zio.getvalue())
    return response

if __name__=='__main__':
    import sys
    filename='/tmp/out.zip'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    print "dumping db to %s " % filename
    f = open(filename,'w')
    f.write(_dump_pageviews_to_sio().getvalue())
    f.close()

