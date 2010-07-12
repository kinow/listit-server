import math
from datetime import datetime as dd  # Stacked Bar Graph Function Helpers
def sBar(filename, user, title='title'):
    DAY_IN_MS = 1000*60*60*24
    COL_SEGMENTS, ROW_GROUPS, GROUP_TYPES = 7,7,5 ## add, edit,edit, del,del
    notes = user.note_owner.all()
    allLogs = ActivityLog.objects.filter(owner=user, action__in=['note-add','note-save','note-delete'])
    data = r.matrix(0,nrow=COL_SEGMENTS, ncol=ROW_GROUPS*GROUP_TYPES) ## 3 cols per weekday, each col segmented into 7 parts/rows
    wksToIndex = lambda rowWeek, colWeek : rowWeek + (colWeek)*COL_SEGMENTS
    nOldEdit = [[] for n in range(ROW_GROUPS)]
    nNewEdit = [[] for n in range(ROW_GROUPS)]
    for log in allLogs:
        noteArr = notes.filter(jid=log.noteid)
        if len(noteArr) < 1:  ## Processing logs for which we still
            continue          ## have the note (deleted or not)
        note = noteArr[0]
        actDate = dd.fromtimestamp(float(log.when)/1000.0)
        actDay = actDate.weekday()
        birthDate = dd.fromtimestamp(float(note.created)/1000.0)
        birthDay = birthDate.weekday()
        firstRecord, lastTime = min(actDate, birthDate ), max(actDate,birthDate)
        startOfDay = dd(lastTime.year, lastTime.month, lastTime.day)
        actTD = firstRecord - startOfDay
        actInPastWk = math.fabs(actTD.days) <= 6 ## Both .created and .when  happened within (current day + 6 previous days)
        if (log.action == 'note-add'):      ## Record Add
            data[wksToIndex(birthDay, actDay*GROUP_TYPES+0)] += 1
            pass
        elif (log.action == 'note-save'):   ## Record Save: Split (edit on day of note.created vs not)
            ##continue if log.noteid in nNewEdit[actDay] else nNewEdit[actDay].append(log.noteid)
            ##if log.noteid in nOldEdit[actDay]: continue
            ##else: nEditProc[actDay].append(log.noteid)
            if actInPastWk:
                if (log.noteid in nNewEdit[actDay]):
                    continue
                else:
                    nNewEdit[actDay].append(log.noteid)
                    data[wksToIndex(birthDay, actDay*GROUP_TYPES+1)] += 1
            else:
                if (log.noteid in nOldEdit[actDay]):
                    continue
                else:
                    nOldEdit[actDay].append(log.noteid)
                    data[wksToIndex(birthDay, actDay*GROUP_TYPES+2)] += 1
        elif (log.action == 'note-delete'): ## Record Death
            if actInPastWk:
                data[wksToIndex(birthDay, actDay*GROUP_TYPES+3)] += 1
            else:
                data[wksToIndex(birthDay, actDay*GROUP_TYPES+4)] += 1
        pass
    r.png(file = '/var/listit/www-ssl/_studywolfe/' + filename + '.png', w=1200,h=800)
    dayNames = ["Mon","Tues","Wed","Thur","Fri","Sat","Sun"]
    colSums = r.colSums(data)
    colMax = r.apply(data, 2, r.max) ## VooDoo !? Returns array of column max values
    colRatios = [int(float(100*colMax[i])/float(colSums[i])) if colSums[i] != 0 else 0 for i in range(ROW_GROUPS*GROUP_TYPES)]
    axisNames = []
    [axisNames.extend([dayNames[i], colRatios[i*GROUP_TYPES+1], colRatios[i*GROUP_TYPES+2], colRatios[i*GROUP_TYPES+3], colRatios[i*GROUP_TYPES+4]]) for i in range(ROW_GROUPS)] 
    subTitle = "Actions: (black) note-add, note-save, note-delete (white)"
    colors = r.c("red", 'orange', 'yellow', 'green', 'blue', 'grey', 'brown')
    title = "#Notes:#Logs:Email:ID -- " + str(notes.count()) + ":" + str(allLogs.count()) + ":" + user.email + ":" + str(user.id)
    r.barplot(data, main=title, ylab='# Action Logs',beside=False, col=colors, space=r.c(3,1,0.1,1,.1), names=axisNames) ## legend=logText
    devoff()


sBar('wt00',gv,"GV's Note Action Periodicities")

def test_wBar(s):
    sBar('wt'+str(s),gv, "GV Note Action Periodicities")            ## Was 6-11 (accidentally over-wrote 6!)
    sBar('wt'+str(s+1),dk, "DK's Note Action Periodicities")
    sBar('wt'+str(s+2),em, "Emax's Note Action Periodicities")
    sBar('wt'+str(s+3),kf, "KatFang's Note Action Periodicities")
    sBar('wt'+str(s+4),ws, "WS's  Note Action Periodicities")
    sBar('wt'+str(s+5),brenn, "Brenn's Note Action Periodicities")

def makeACUBarPlots():
    i=0
    path = 'acu/rhythms/weekly_3/userid-'
    print "Start time: ", time.gmtime()
    for user in u[750:]:
        uNotes = n.filter(owner=user)
        uLogs = ActivityLog.objects.filter(owner=user, action__in=['note-add','note-save','note-delete'])
        if (((uNotes.count() >= 120) or (uLogs.count() >= 120)) and ((uNotes.count() >= 50) and (uLogs.count() >= 50))):
            sBar(path + str(user.id), user)
            i += i
            pass
        pass
    print "Users processed: ", str(i) , " out of: ", str(len(u))
    print "Finish time: ", time.gmtime()

