python manage.py shell

## startup
from django.contrib.auth.models import User
from jv3.models import *
from jv3.utils import *
import jv3.study.content_analysis as ca
import jv3.study.ca_datetime as cadt
import jv3.study.ca_sigscroll as cass
import jv3.study.ca_load as cal
import jv3.study.ca_plot as cap
import jv3.study.ca_search as cas
import rpy2
import rpy2.robjects as ro
from jv3.study.study import *
from numpy import array
import random
r = ro.r
em = User.objects.filter(email="emax@csail.mit.edu")[0]
emn = Note.objects.filter(owner=em)
ws = User.objects.filter(email='wstyke@gmail.com')
emax2 = User.objects.filter(email="electronic@gmail.com")[0]
brenn = User.objects.filter(email="brennanmoore@gmail.com")[0]
gv = User.objects.filter(email="gvargas@mit.edu")[0]
devoff = lambda : r('dev.off()')
c = lambda vv : apply(r.c,vv)


## consenting users 
u = [ us for us in User.objects.all() if is_consenting_study2(us)]
## consenting notes
n = Note.objects.filter( owner__in=[ u for u in User.objects.all() if is_consenting_study2(u)] )

## Returns array of property values for entityArray
def arr_prop(objArray, prop):
    return [float(x) for x in objArray.values_list(prop, flat=True)]

def get_rand_user():
    ru = u[random.randint(0,len(u))]
    notes = Note.objects.filter(owner=ru)
    return (user, notes)

def plot_xyz(filename,x,y,z, xl="x",yl="y",title="title"):
    r.png(file = '/var/listit/www-ssl/_studywolfe/' + filename + '.png', w=3200,h=1600)
    r.plot(x,y,cex=z,xlab=xl,ylab=yl,main=title)
    devoff()



def ezPlot(filename, x,y,z, xl="x",yl="y",title="title"):
    xd, yd, zd = c(x), c(y), c(z)
    plot_xyz(filename, xd, yd, zd, xl, yl, title)   


## Given ONE user's notes, plot note attribute (created) vs activitylog attribute (when)
def aPlot(filename, notes,  xProp, logProp, logTypes, xl='x', yl='y', title='title'):
    x, y, z = [], [], []
    allLogs = ActivityLog.objects.filter(owner=notes[0].owner, action__in=logTypes)
    for log in allLogs:
    	noteArr = notes.filter(jid=log.noteid)
        if len(noteArr) != 1:
    	   continue
  	## We have a single note found
	note = noteArr[0]
	x.append(note.created)
	y.append(log.when)
    ## Now we have a list of notes and logs
    x = [float(v) for v in x]
    y = [float(v) for v in y]    
    ezPlot(filename, x,y,[1]*len(x),xl, yl, title)

## X-Y Scatter Plots with bubble size fixed
def bPlot(filename, x, xProp, y, yProp, size=1, xl='x', yl='y', title='title'):
    xd = c(arr_prop(x, xProp))
    yd = c(arr_prop(y, yProp))
    zd = c([size]*len(x))
    plot_xyz(filename, xd, yd, zd, xl, yl, title)

## X-Y Scatter plots with specified bubble sizes
def cPlot(filename, x, xProp, y, yProp, z, zProp, xl='x', yl='y', title='title'):
    xd = c(arr_prop(x, xProp))
    yd = c(arr_prop(y, yProp))
    zd = c(arr_prop(z, zProp))
    plot_xyz(filename, xd, yd, zd, xl, yl, title)




## Specific Plots using above general plots


## Plots note-add and note-edits on a x=created, y=edited graph
## - Vertical row of dots   = one note being edited a bunch
## - Horizontal row of dots = one time when a bunch of notes edited

def plot_note_edits(filename, notes):
    username = notes[0].owner.email
    aPlot("note_edits/" +filename, notes, 'created', 'when', ['note-save', 'note-add'], 'created', 'when', 'Created vs When-Log-Entry-Recorded for '+username)


## Given ONE user's notes, plot note attribute (created) vs activitylog attribute (when)
def mPlot(filename, notes,  title='title'):
  points = {'note-add':r.c(),'note-save':r.c(),'note-delete':r.c()}
  r.png(file = '/var/listit/www-ssl/_studywolfe/' + filename + '.png', w=3600,h=1800)
  allLogs = ActivityLog.objects.filter(owner=notes[0].owner, action__in=['note-add','note-save','note-delete'])
  for log in allLogs:
     noteArr = notes.filter(jid=log.noteid)
     if len(noteArr) < 1:
         continue
     note = noteArr[0]
     points[log.action] = r.rbind(points[log.action],c([float(note.created),float(log.when)]))
     pass
  r.plot(points['note-add'], cex=6.0,col = "orange", pch='.', xlab='created', ylab='action', main=title)
  r.points(points['note-save'], cex=1.0,col = "purple", pch='o')
  r.points(points['note-delete'], cex=1.0,col = "dark red", pch='x')
  devoff()


## + Added lines from mPlot
## Given ONE user's notes, plot note attribute (created) vs activitylog attribute (when)
def mmPlot(filename, notes,  title='title'):
    points = {'note-add':r.c(),'note-save':r.c(),'note-delete':r.c()}
    births = {}
    deaths = {}
    today = time.time()*1000.0
    r.png(file = '/var/listit/www-ssl/_studywolfe/' + filename + '.png', w=3200,h=1600)
    allLogs = ActivityLog.objects.filter(owner=notes[0].owner, action__in=['note-add','note-save','note-delete'])
    for log in allLogs:
    	noteArr = notes.filter(jid=log.noteid)
	if len(noteArr) < 1:
	   continue
	note = noteArr[0]
	## birth/deahts
	births[note.jid] = note.created
	if not note.deleted and note.jid not in deaths:
	   deaths[note.jid] = today
       	   pass
     	if (log.action == 'note-delete'):
           deaths[note.jid] = float(log.when)
     	points[log.action] = r.rbind(points[log.action],c([float(note.created),float(log.when)]))
     	pass
    r.plot(points['note-add'], cex=1.0,col = "green", pch='o',xlab='',ylab='')
    r.points(points['note-save'], cex=1.0,col = "orange", pch='o')
    r.points(points['note-delete'], cex=1.0,col = "dark red", pch='x')
    #r.lines( reduce(r.rbind,[r.c(float(births[x]),float(deaths[x])) for x in births.keys() if x in deaths],r.c()), col = "dark red")
    for x in births.keys():
    	if x in deaths:
           if today - deaths[x] < 0.001 :
	      color = 'green'
           else:
	      color = 'black'
	r.lines(c([float(births[x])]*2),c([float(births[x]),float(deaths[x])]), col=color)
        pass
    devoff()

## Given ONE user's notes, plot note attribute (created) vs activitylog attribute (when)
def mmmPlot(filename, notes,  title='title'):
  ## Meta-data for title
  allLogs = ActivityLog.objects.filter(owner=notes[0].owner, action__in=['note-add','note-save','note-delete'])
  useremail = notes[0].owner.email
  noteCount = notes.count()
  actionCount = allLogs.count()
  title = "#Notes:#Logs:Email -- " + str(noteCount) + ":" + str(actionCount) + ":" + useremail 
  ## Meta-data for points
  points = {'note-add':r.c(),'note-save':r.c(),'note-delete':r.c()}
  births = {}
  deaths = {}
  today = time.time()*1000.0
  r.png(file = '/var/listit/www-ssl/_studywolfe/' + filename + '.png', w=3200,h=1600)
  minCreatedMSEC, maxCreatedMSEC = 0, 0
  minActionMSEC, maxActionMSEC = 0, 0
  for log in allLogs:
     noteArr = notes.filter(jid=log.noteid)
     if len(noteArr) < 1:
        continue
     note = noteArr[0]
     minCreatedMSEC = min(minCreatedMSEC, note.created)
     maxCreatedMSEC = max(maxCreatedMSEC, note.created)
     minActionMSEC = min(minActionMSEC, log.when)
     maxActionMSEC = max(maxActionMSEC, log.when)
     ## birth/deahts
     births[note.jid] = note.created
     if not note.deleted and note.jid not in deaths:
        deaths[note.jid] = today
        pass
     if (log.action == 'note-delete'):
        deaths[note.jid] = float(log.when)
     points[log.action] = r.rbind(points[log.action],c([float(note.created),float(log.when)]))
     pass
  r.plot(points['note-add'], cex=1.0,col = "green", pch='o',xlab='Created Date',ylab='Action Date', main=title)
  r.points(points['note-save'], cex=2.0,col = "purple", pch=17)
  r.points(points['note-delete'], cex=2.0,col = "dark red", pch='x')
  #r.lines( reduce(r.rbind,[r.c(float(births[x]),float(deaths[x])) for x in births.keys() if x in deaths],r.c()), col = "dark red")
  xWks = (maxCreatedMSEC - minCreatedMSEC) / (1000*60*60*24*7)
  yWks = (maxActionMSEC - minActionMSEC) / (1000*60*60*24*7)
  r.grid(nx=int(xWks), ny=int(yWks), col="black", lwd=1)
  for x in births.keys():
     if x in deaths:
        if today - deaths[x] < 0.001 :
           color = 'green'
        else:
           color = 'black'
        r.lines(c([float(births[x])]*2),c([float(births[x]),float(deaths[x])]), col=color)
        pass
  devoff()

mmmPlot('wt0',emn)


## Plot up to 100 users who satisfy conditions
i=0
path = 'acu/note_life2/'
print "Start time: ", time.gmtime()
startTime = time.time()
for user in u:
    uNotes = Note.objects.filter(owner=user)
    uLogs = ActivityLog.objects.filter(owner=user, action__in=['note-add','note-save','note-delete'])
    if (((uNotes.count() >= 120) or (uLogs.count() >= 120)) and ((uNotes.count() >= 50) and (uLogs.count() >= 50))):
       mmmPlot(path+str(i)+"-"+str(user.id), uNotes)
       i += 1

print "Users processed: ", str(i) , " out of: ", str(len(u))
print "Finish time: ", time.gmtime()
finishTime = time.time()

