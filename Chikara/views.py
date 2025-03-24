from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from Chikara.settings import BASE_DIR, STATIC_ROOT
from random import randint
import mysql.connector
import json,hashlib
import urllib.parse
import sys,time,datetime
from ossapi import Ossapi
from dbview.models import *
import sys,json


#Before using this please set these up at /etc/Chikara/config.conf
for cfg in open("/etc/Chikara/config.conf").read().split("\n"):
    key = cfg.split("=")
    if key[0] == "client_id":
        client_id = key[1]
    elif key[0] == "client_secret":
        client_secret = key[1]

starttime=time.time()
perfbom=0.035
dedipoints=0.00000727
maxperf=3760*3
nom=2
bio = "test"
pointsbase=1
mainurl='https://dev.catboy.best'
beatmapapi=mainurl+'/api/v2/'
allowspoof=0
gradecolour=(81, 149, 194),(114, 123, 179),(105, 173, 99),(113, 85, 173),(173, 136, 61),(168, 70, 50),(20,20,20)
modsaliasab='AT','DT','HT','SL','BT','RND', # Mods Alias
medals=("The End","You've made it"),("Baby Steps","Welcome to the Game"),(">~<","Impressive"),('Psycho','Dang you can read that?!'),('Welcome back Veteran','Glad to see you back'),('D-Ranker','Unrhythmic'),('S-Ranker','Like to show off. huh?'),('Donator','Thanks for Supporting the Game!'),('Sniper','First Comes, First Serve!'),('BreakThrough','Unstoppable'),('Top 100','You are the chosen one'),('Top 50','Almost There'),('Top 10','Grab some Popcorn 🍿'),('Top 1,000','Still a Virgin at this game are you?'),('Lorem Ipsum',"Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.") # Medals
leveltemp=0.0000005 # Level multiplier
username='0' # Guest mode
issignin=False # Sign in state
allowsubmissions = 1


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="qluta",
        password="Qlutaismyfav$23",
        database='qluta'
    )

mydb = connect_db()
mycursor = mydb.cursor(buffered=True, dictionary=True)
def fetch_beatmap(beatmapidset,beatmapid):
    api = Ossapi(client_id, client_secret)
    if int(beatmapidset) != 0 and int(beatmapid) != 0:
        beatset = api.beatmapset(int(beatmapidset))
        beatmaps = beatset.beatmaps
        difficulty = None
        for a in beatmaps:
            if int(beatmapid) == a.id:
                exists = 1
                difficulty = a.version
                break
        if exists:
            title = beatset.title
            titleuni = beatset.title_unicode
            artist = beatset.artist
            artistuni = beatset.artist_unicode
            bpm = beatset.bpm
            creator = beatset.creator
            ranked = beatset.ranked.value
            if ranked < 4 and ranked > 0:
                ranked = 1
            elif ranked == 4:
                ranked = 2
            else:
                ranked = 0
            info = {
                "title" : title,
                "titleuni" : titleuni,
                "artist" : artist,
                "artistuni" : artistuni,
                "difficulty" : difficulty,
                "creator" : creator,
                "ranked" : ranked,
                "bpm" : bpm,
                "exist" : 1
            }
    else:
        info = {
            "title" : None,
            "titleuni" : None,
            "artist" : None,
            "artistuni" : None,
            "difficulty" : difficulty,
            "creator" : None,
            "ranked" : None,
            "bpm" : None,
            "exist" : 0
        }
    return info



def getspp(offset=0,limit=0):
    tols=offset
    tan=0
    pp=28000+(len(open('userlist').read().rstrip('\n').split('\n')))
    pp-=(2*tols)*tols
    tab=0
    st=8.5
    tick=0
    shutdown=0
    if not limit:
        limit=len(open('userlist').read().rstrip('\n').split('\n'))
    elif limit==-1:
        shutdown=1
    else:
        limit=limit+offset
    if allowspoof and not shutdown:
        for a in open('userlist').read().rstrip('\n').split('\n')[::-1][offset:limit]:
            tols+=1
            name=a
            pp-=2*tols
            if pp<1:
                pp=0
                break
            yield name,pp

def getstat(command, useris, raw=False, page=1):  # Added leveltemp parameter with default value
    if command == 'score':
        user = User.objects.filter(username=useris).first()
        t = user.ranked_score if user and user.ranked_score is not None else 0
    elif command == 'level':
        user = User.objects.filter(username=useris).first()
        ranked_score = user.ranked_score if user and user.ranked_score is not None else 0
        t = int(int(ranked_score) * leveltemp)
    
    elif command == 'rank':
        user = User.objects.filter(username=useris).first()
        t = user.ranking if user else None
    
    elif command == 'ranking':
        tols = 0
        users = []
        
        # Get users from DB ordered by ranked_points
        db_users = User.objects.all().order_by('-ranked_points')[50*(page-1):50*page]
        
        for a in db_users:
            try:
                if a.ranked_points:
                    tols += 1
                    users.append(a)
            except AttributeError:
                pass
        
        if tols == 50:
            limit = -1
        else:
            limit = 50 - tols
        return users, tols
    
    elif command in ['accuracy', 'max', 'great', 'meh', 'bad', 'max_combo']:
        user = User.objects.filter(username=useris).first()
        t = getattr(user, command) if user else None
    
    elif command == 'full':
        data = {
            "rank": getstat('rank', useris),
            "points": getstat('points', useris),
            "score": getstat('score', useris),
            "accuracy": getstat('accuracy', useris),
            "level": getstat('level', useris),
            "donator": False,
            "restricted": False
        }
        
        if not raw:
            import json
            t = json.dumps(data)
        else:
            t = data
    
    elif command == 'points':
        user = User.objects.filter(username=useris).first()
        t = user.ranked_points if user else None
    
    if t is None:
        t = 0
        
    return t# Add multiplier of a mod to the performance

def getmult(multiplier,submit=False):
    if not submit:
        try:
            multiplier=float(multiplier)
            #multiplier=1
            newmodsys=0
        except Exception:
            fulltmp=multiplier
            multiplier=1
            newmodsys=1
    else:
        return multiplier
        newmodsys=1
        multiplier=1
    if newmodsys:
       for a in modsaliasab:
            if a in str(fulltmp):
               if a=='BT':
                  multiplier*=1.15
               elif a == 'DT':
                  multiplier*=1.15
               elif a == 'HT':
                  multiplier/=0.3
               elif not a in ('RND','AT'):
                  multiplier+=0.5
    return multiplier


def getpoint(perfect,good,meh,bad,multiplier,combo=1,type=int): # Points System 2024/06/15
    ppvalue = 0
    ppvalue = perfect * perfbom
    ppvalue -= perfbom/2 * good
    ppvalue -= perfbom/3 * meh
    ppvalue -= perfbom * bad
    ppvalue += combo * perfbom
    ppvalue *= multiplier
    if type == int:
        return ppvalue
    else:
        return str(ppvalue)
    
def getmedals(user):
    medco=0
    donator=0
    rank=int(getstat('rank',user))
    points=int(getstat('points',user))
    score=int(getstat('score',user))
    level=int(score*leveltemp)
    if level<1:
        level=1
    accuracy=getstat('accuracy',user)
    max=getstat('max',user)
    great=getstat('great',user)
    meh=getstat('meh',user)
    bad=getstat('bad',user)
    max_combo=getstat('max_combo',user)
    for title,desc in medals:
        show=0
        if medco==0 and rank==1:
            show=1
        elif medco==1 and points>1:
            show=1
        elif medco==3 and points>1000:
            show=0
        elif medco==2 and max_combo>1000:
            show=1
        elif medco==5 and bad>1000:
            show=1
        elif medco==6 and max>1000:
            show=1
        elif medco==7 and donator:
            show=1
        elif medco==13 and rank and rank<=1000:
            show=1
        elif medco==10 and rank and rank<=100:
            show=1
        elif medco==11 and rank and rank<=50:
            show=1
        elif medco==12 and rank and rank<=10:
            show=1
        medco+=1
        yield (title,desc,show)

# Querying scores

def getscores(user='',beatmapid=0,orderbybiggest=False,limit=30):
    tols=0
    if orderbybiggest:
        strip='points'
    else:
        strip='created'
    if user=='':
        if beatmapid!=0:
            score = Score.objects.values().filter(beatmap_id=beatmapid)[:limit]
        else:
            score = Score.objects.values().order_by(f"-{str(strip)}")[:limit]
    else:
        score = Score.objects.filter(username=user).values().order_by(f"-{str(strip)}")[:limit]
    per=1
    for a in score:
        mods=a['mods']
        a['multiplier']=getmult(mods)
        a['points']=getpoint(a['max'],a['great'],a['meh'],a['bad'],a['multiplier'], a['combo'])
        a['weighted_pp']=a['points']*per#*(tmp[15]*2)
        
        if user in a['username'] or beatmapid in a['beatmap_id']:
            yield a
        tols+=1
        per-=0.02
    if not tols:
        return 0

def timeform(t): # Parses time and date to a human readable format
    if t==None:
        return 'Never Played'
    if t>=31536000:
        x=int(t//31536000)
        fix='Year'
    elif t>=2630000:
        fix='Month'
        x=int(t//2630000)
    elif t>=86400:
        x=int(t//86400)
        fix='Day'
    elif t>=3600:
        x=int(t//3600)
        fix='Hour'
    elif t>=60:
        x=int(t//60)
        fix='Minute'
    elif t<60:
        x=int(t)
        fix='Second'        
    if x>1:
        fix+='s'
    return str(x)+' '+str(fix)+' Ago'


# User score Front UX parser
def get_userscore(user='',recent=True,mini=False,limit=50):
    tols=0
    pek=1
    peak = ''
    timeest = ''
    if recent:
        scorecard = open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/scorecardtemplate.html").read()
    else:
        scorecard = open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/scoreweightedcard.html").read()
    for tmp in getscores(user=user,orderbybiggest=not recent,limit=limit):
        tols+=1
        acc=round(((tmp['max']+(tmp['great']/2)+(tmp['meh']/3))/(tmp['max']+tmp['great']+tmp['meh']+tmp['bad']))*100,2)
        if acc>=100:
            gradet='SS'
        elif acc>95 and not tmp['bad']:
            gradet='S'
        elif acc>90:
            gradet='A'
        elif acc>85:
            gradet='B'
        elif acc>69:
            gradet='C'
        elif acc<1:
            gradet='?'
        else:
            gradet='D'
        try:
            timeest = timeform(time.time()-float(tmp['created'].timestamp()))
        except Exception as error:
            timeest = 'Error Processing Time:' + str(error) + ' ' + str(tmp['created'])
        weighted = str(int(tmp['weighted_pp']))
        weightedp = str(int(pek*100))
        modse=''
        for a in modsaliasab:
            if a in tmp['mods']:
                modse += f'<span class="mod">{a}</span>'
        peak += scorecard.replace("{date}",timeest).replace("{title}",tmp['beatmapname']).replace("{artist}",tmp['artist']).replace("{rank}",gradet).replace("{difficulty}",tmp['beatmapdiff']).replace("{points}",str(int(getpoint(tmp['max'],tmp['great'],tmp['meh'],tmp['bad'],tmp['multiplier'],combo=tmp['combo'])))).replace("{weighted_points}",weighted).replace("{weighted_percentage}",weightedp).replace("{mods}",modse)
        pek-=0.02
    if tols==0:
        peak +='<h3 class="bar">No Recent Plays -n-</h3>'
    return peak

# Playtime parse

def playtime(t):
    if t==None:
        return 'Never Played'
    t=int(t)
    if t==0:
        return '0h 0m'
    hour=t//3600
    t-=3600*hour
    min=t//60
    t-=60*min
    sec=t
    return str(hour)+'h '+str(min)+'m '+str(sec)+'s'

# Checking Login

def checklogin(usr,pwd,signup=False,id=0):
    #html += "SELECT * FROM users WHERE username = %s", (usr,))
    #return 1
    if usr in ('None','Guest'):
        return (0,0)
    try:
        id=int(id)
        id=0
    except Exception:
        id=0
    fake=0
    if signup:
        mycursor.execute("SELECT * FROM users WHERE username = %s OR id = %s", (usr,id))
        if allowspoof:
            for a in open('userlist').read().rstrip('\n').split('\n'):
                if usr==a:
                    result={'username':a,'password':None}
                    fake=1
                    break
    else:
        mycursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (usr,pwd))
    if not fake:
        result = mycursor.fetchone()
    if result!=None:
        if not signup:
            p=str(result['password'])
            if pwd==p:
                result=1
            else:
                result=0
    else:
        result=0
    if result:
        return (1,fake)
    else:
        return (0,fake)

# API

def api(request,command):
    command=command.split('/')
    if len(command)>0 and request.method == "POST":
        if command[0]=='signup':
            try:
                login=login[1].split('&')
                login[2]=hashlib.sha256(bytes(login[2],'utf-8')).hexdigest()
                if not checklogin(login[0],'',signup=True)[0]:
                    sys.stdout.write('1')
                else:
                    sys.stdout.write('0')
            except Exception as error:
                print(error)
        elif command[0]=='login':
            try:
                username = request.POST.get("username")
                password = request.POST.get("password")
                password = hashlib.sha256(bytes(password,'utf-8')).hexdigest()
                accept=checklogin(username, password)[0]
                
                # Process the credentials (authentication logic here)
                if accept:  # Example check
                    response = JsonResponse({"success": True}, status=200)
                    response.set_cookie("username", username, max_age=31536000)
                    response.set_cookie("password", password, max_age=31536000)
                else:
                    response =  JsonResponse({"success": False}, status=401)
            except json.JSONDecodeError:
                response = JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
            return response
    elif len(command)>0 and request.method == "GET":
        if command[0]=='listmedal':
            username=command[1]
            data=[]
            try:
                for title,desc,gotit in getmedals(username):
                    data.append({'title':title,'desc':desc,'achieved':gotit})
                return HttpResponse(json.dumps(data))
            except Exception as err:
                return HttpResponse(err)
        elif command[0]=='createroom':
            login=command[1:]
            currently=urllib.parse.unquote(login[5])
            beatmapid=login[4]
            beatmapsetid=login[3]
            roomname=urllib.parse.unquote(login[2])
            password=login[1]
            username=login[0]
            if checklogin(username,password):
                print(login)
                mycursor.execute("INSERT INTO multiplayer (room_name,currently_playing,player_list,host,state) VALUES (%s,%s,%s,%s,%s)",(roomname,currently,username+';',username,1))
                mydb.commit()
        elif command[0]=='getmultilist':
            try:
                mycursor.execute("SELECT id,room_name,currently_playing,player_list,host,state FROM multiplayer ORDER BY created DESC LIMIT 5")
                multilist=mycursor.fetchall()
                #print(multilist)
                #print({'name':'Lv. 15-629 Maps ONLY','current_players':36,'currently_playing':'DJ Dril4 - Nut Mommy'},{'name':'Lv. 3-10 Maps ONLY','current_players':653,'player_limit':9999,'currently_playing':'DJ Dril4 - Nut Mommy [CREEPER]'},)
                #multilist=()
                print(json.dumps(multilist))
            except Exception as err:
                print(err)
        elif command[0]=='getbeatmap':
            exit()
            print(json.dumps({'RankedStatus':1,'BPM':19000}))
        elif command[0]=='getleaderboard':
            print(json.dumps(get_leaderboard(login[1])))
#            for a in result:
#                print(a)
        elif command[0]=='menunotice':
            f=open('motd').read().rstrip('\n').split('\n')
            r=randint(1,len(f))
            return HttpResponse(f[r-1])
        elif command[0]=='setstatus':
            #print(login)
            accept=0
            if checklogin(login[1],'x',signup=True)[0]:
                accept=1
            if accept:
                if login[2]=='playing':
                    mycursor.execute("UPDATE users SET stattime = %s, status = %s WHERE username = %s",(int(time.time()),urllib.parse.unquote(login[3]),login[1]))
                    mydb.commit()
#                    print(login[3])
#                    with open(profiledb+login[1]+'/status','w') as x:
                        #if login[3]=='None':
#                        x.write('playing '+str(urllib.parse.unquote(login[3])))
        elif command[0]=='chkprofile':
            msg=''
            usrpwd=request.META.get('HTTP_USERNAME', ''),request.META.get('HTTP_PASSWORD', '')
            if checklogin(usrpwd[0],usrpwd[1])[0]:
                ac=1
            else:
                ac=0
            prompt={'success':ac,'notification':msg}
            return JsonResponse(prompt)


        elif command[0]=='getstat':
            #print(login)
            accept=0
            t=0
            user = request.META.get('HTTP_USERNAME', '')
            if checklogin(user,'x',signup=True)[0]:
                accept=1
            if accept:
                if command[1] == "full":
                    raw=True
                else:
                    raw=False
                t=getstat(command[1],user,raw=raw)
                return JsonResponse(t)
            else:
                return JsonResponse({"error":1})
        elif command[0]=='submitscore':
            try:
#                try:
#                    taken=score[13]
#                except Exception:
#                    taken=0
                accept=0
                user = request.META.get("HTTP_USERNAME","")
                #print(score)
                test=checklogin(user,request.META.get("HTTP_PASSWORD",""))[0]
                if test and allowsubmissions:
                    accept=1
                    #print('Submitted as',score[0])
                else:
                    if not test:
                        return HttpResponse('Incorrect Credentials')
                    else:
                        return HttpResponse('Submissions are disabled')
                if accept and allowsubmissions:         
                   # ORDER BY points DESC 
                   try:
                       taken=int(request.META.get("HTTP_TAKEN",""))
                   except Exception:
                       taken=0
                   mods = getmult(request.META.get("HTTP_MODS",""),submit=True)
                   mult=getmult(mods)
                   combo = int(request.META.get("HTTP_COMBO",""))
                   smax = int(request.META.get("HTTP_MAX",""))
                   sgreat = int(request.META.get("HTTP_GREAT",""))
                   smeh = int(request.META.get("HTTP_MEH",""))
                   sbad = int(request.META.get("HTTP_BAD",""))
                   points=getpoint(smax,sgreat,smeh,sbad,float(mult),combo=combo)
                   beatmap_id = int(request.META.get("HTTP_BEATMAPID",""))
                   beatmapset_id = int(request.META.get("HTTP_BEATMAPSETID",""))
                   maxpoints=getpoint(smax+sgreat+smeh+sbad,0,0,0,float(mult),combo=combo)
                   finalscore=(points/maxpoints)*(1000000*mult)
                   mycursor.execute("SELECT * FROM beatmaps WHERE osubeatmapid = %s AND osubeatmapsetid = %s", (beatmap_id, beatmapset_id))
                   info = mycursor.fetchone()
                   if info == None:
                        info = fetch_beatmap(beatmapset_id,beatmap_id)
                        if info["exist"]:
                            mycursor.execute("INSERT INTO beatmaps (title, title_unicode, artist, artist_unicode, difficulty, BPM, ranked, mapper, osubeatmapid, osubeatmapsetid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(info["title"],info["titleuni"],info["artist"],info["artistuni"], info["difficulty"], info["bpm"],info["ranked"],info["creator"],int(beatmap_id),int(beatmapset_id)))
                            mydb.commit()
                            ranked = info["ranked"]
                        else:
                            ranked = 0
                   else:
                        ranked = info["ranked"]
                   if not float(points)>maxperf and accept and ranked > 0:
                        mycursor.execute("SELECT * FROM scores WHERE beatmap_id = %s AND username = %s ORDER BY points DESC ", (beatmap_id, user))
                        tmp=mycursor.fetchone()
                        if not tmp==None:
                            #print(float(data[3]),tmp['points'])
                            oldmult=getmult(getmult(tmp["mods"],submit=True))
                            if points > float(getpoint(tmp["max"],tmp["great"],tmp["meh"],tmp["bad"],oldmult)):# and usr['ranked_points']!=None and usr['ranked_points']+11<=float(data[3]):
                                mycursor.execute("DELETE FROM scores WHERE beatmap_id = %s AND username = %s", (beatmap_id, user))
                                submit=True
                            else:
                                submit=False
                        else:
                            submit=True
                        mycursor.execute("SELECT * FROM users WHERE username = %s", (user,))
                        usr=mycursor.fetchone()
                        if submit:
                            scoreentry = (user, info["title"],info["artist"],points, combo, beatmap_id, beatmapset_id, smax,sgreat,smeh,sbad, info["difficulty"],mods, maxpoints)
                            mycursor.execute("INSERT INTO scores (username, beatmapname, artist, points, combo, beatmap_id, beatmapset_id, max, great, meh, bad, beatmapdiff, mods, maxpoints) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", scoreentry)
                            mydb.commit()
                        tmp=usr
                        # ACC

                        hits=[0,0,0,0]
                        b=1
                        for a in getscores(user=user,orderbybiggest=True,limit=50):
                            hits[0]+=a['max']
                            hits[1]+=a['great']
                            hits[2]+=a['meh']
                            hits[3]+=a['bad']
                        t=round(((hits[0]+(hits[1]/2)+(hits[2]/3))/(hits[0]+hits[1]+hits[2]+hits[3]))*100,2)
                        mycursor.execute("UPDATE users SET accuracy = %s WHERE username = %s", (t,user))
                        mycursor.execute("UPDATE users SET max = %s WHERE username = %s", (hits[0],user))
                        mycursor.execute("UPDATE users SET great = %s WHERE username = %s", (hits[1],user))
                        mycursor.execute("UPDATE users SET meh = %s WHERE username = %s", (hits[2],user))
                        mycursor.execute("UPDATE users SET bad = %s WHERE username = %s", (hits[3],user))
                        # Combo

                        mycursor.execute("SELECT * FROM scores WHERE username = %s ORDER BY combo DESC ", (user,))
                        result = mycursor.fetchone()
                        max_combo=result['combo']
                        mycursor.execute("UPDATE users SET max_combo = %s WHERE username = %s", (max_combo,user))
                        # Points
                        rankedpoints=0
                        x=0
                        for a in getscores(user=user,orderbybiggest=True,limit=50):
                            try:
                                al=int(a['weighted_pp'])
                                x+=1
                                rankedpoints+=int(al)
                            except Exception as err:
                                sys.stdout.write(str(err))
                        rankedscore=tmp['ranked_score']
                        if rankedscore:
                            t+=(int(rankedscore)+int(finalscore))*dedipoints
                        users=[]
                        mycursor.execute("SELECT username,ranked_points FROM users ORDER BY ranked_points DESC")
                        for a in mycursor.fetchall():
                            name=a['username']
                            pp=a['ranked_points']
                            if not pp:
                                pp=0
                            users.append((name,pp))
                        if allowspoof:
                            for name,pp in getspp():
                                users.append((name,pp))
                            users=sorted(users, key=lambda x: x[1],reverse=True)
                        rankb=1
                        for a in users:
                            if a[0]==user:
                                break
                            rankb+=1
                        ranking=rankb
                        mycursor.execute("UPDATE users SET ranked_points = %s WHERE username = %s", (rankedpoints,user))
                        mycursor.execute("UPDATE users SET ranking = %s WHERE username = %s", (ranking,user))
                        if tmp['playtime']==None:
                            mycursor.execute("UPDATE users SET playtime = %s WHERE username = %s", (int(taken),user))
                        else:
                            mycursor.execute("UPDATE users SET playtime = playtime + %s WHERE username = %s", (int(taken),user))
                        if tmp['ranked_score']==None:
                            mycursor.execute("UPDATE users SET ranked_score = %s WHERE username = %s", (int(finalscore),user))
                        else:
                            mycursor.execute("UPDATE users SET ranked_score = ranked_score + %s WHERE username = %s", (int(finalscore),user))
                        mydb.commit()
                        return JsonResponse({"rank": ranking,"points": rankedpoints,"rankedmap": info["ranked"],"error": 0})
                   else:
                        return HttpResponse('Forbidden Score')
                    #print(score)
            except Exception as err:
                return HttpResponse(str(['ERR',err,'Line '+str(sys.exc_info()[-1].tb_lineno)]))
#               with open(scoresdb,'a') as x:
#                    if not int(float(scoresep[2]))>1000:
#                        x.write(scorestr+'\n')
        else:
            return HttpResponse('Unknown Command')
    else:
        return HttpResponse('(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Welcome to Chikara!')


# User Page

def header(request):
    head = open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/header.html").read()
    accept=checklogin(request.COOKIES.get('username', None), request.COOKIES.get('password', None))[0]
    if accept:
        head = head.replace("{usertag}", request.COOKIES.get('username'))
    else:
        head = head.replace("{usertag}", "Guest")
    return head

def user(request, user):
    tickle= time.time()
    html = header(request) + open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/userpage.html").read()
    usertest = checklogin(user,'x',signup=True,id=user)
    if usertest[0]:
        if user=='aquapoki':
            emblem='Dev',
            donator=1
        elif user=='Beatsu':
            emblem='JBF!','Dev'
            donator=1
        else:
            emblem=''
            donator=0
        if not usertest[1]:
            html = html.replace('{sitetitle}',f"{user}'s Profile")
            mycursor.execute("SELECT * FROM users WHERE username = %s", (user,))
            tmp=mycursor.fetchone()
            try:
                rank=int(tmp["ranking"])
                points=int(getstat('points',user))
                score=int(getstat('score',user))
                level=int(score*leveltemp)
                if level<1:
                    level=1
                accuracy=getstat('accuracy',user)
                max=getstat('max',user)
                great=getstat('great',user)
                meh=getstat('meh',user)
                bad=getstat('bad',user)
            except Exception as err:
                html += str(err)
            minnum=0
            for a in getscores(user=user,orderbybiggest=True,limit=50):
                minnum+=1
            if rank<1:
                rank=None
            max_combo=getstat('max_combo',user)
            if rank:
                finalrank=format(rank,',')
            else:
                finalrank='?'
            html += '<div class="containerbox">'
            html += open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/usernamecard.html").read().replace("{rank}",str(rank)).replace('{username}',tmp['username']) # User name card

            html += '<div class="cardcontainer spacetop spacebottom">'
            html += '<span>'
            try:
                if (tmp['stattime'],tmp['status'])!=(None,None) and not time.time()-tmp['stattime']>300:
                    html += tmp['status']
                else:
                    html += 'Last Seen '+str( timeform(time.time()-tmp['stattime']))
            except Exception as err:
                html += 'New player <3'
            html += '</span></div>' # Status Card
            html += '<div class="cardcontainer spacetop spacebottom">'
            html += '<div class="title">Stats</div>'
            html += '<div style="display:flex;">'
            if level>0:
                html += '<h1 style="margin-top:0px;margin-bottom:35px;flex: 1;" class="box">Level '+str(format(level,','))+'</h1>'
            
            html += '<div style="text-align:right;"'

            html += '<br>Ranked Points:  <span class="bar">'
            html += str(format(points,','))+'pp</span><br></br>'#Ranked Score:  ')
#            html += '<span class="bar">')
#            html += str(format(int(getstat('score',user)),','))+'</span>')
            html += 'Total Play Time: '
            html += '<span class="bar">'
#            html += tmp)
            html += str(playtime(tmp['playtime']))+'</span><br></br>'
            if score>0:
                html += 'Ranked Score: '
                html += '<span class="bar">'
                html += str(format(score,','))+'</span><br></br>'
            html += 'Accuracy: '
            html += '<span class="bar">'
            html += str(round(accuracy,2))+'%</span><br></br>'
            html += 'Total MAX: '
            html += '<span class="bar">'
            html += str(max)+'</span><br></br>'
            html += 'Total GREAT: '
            html += '<span class="bar">'
            html += str(great)+'</span><br></br>'
            html += 'Total MEH: '
            html += '<span class="bar">'
            html += str(meh)+'</span><br></br>'
            html += 'Total BAD: '
            html += '<span class="bar">'
            html += str(bad)+'</span><br></br>'
            html += 'Max Combo: '
            html += '<span class="bar">'
            html += str(max_combo)+'x</span><br></br>'
            if tmp['username']=='aquapoki':
                html += 'Virgin Meter: '
                html += '<span class="bar">'
                html += '69.420%</span><br></br>'
            html += "</div>"
            if issignin and username=='aquapoki':
                html += '<a href="/recentplay"><button class="minibutton">Recent Plays</button></a></span>'
            html += '</br></div></div>' # Ends Stats Section
            html += '<div style="display:flex;flex-wrap: wrap;align-content:center;" class="cardcontainer spacetop spacebottom">'
            medco=0
            for title,desc,show in getmedals(user):
                if show:
                    suf=''
                else:
                    suf='opacity:20%;'
                html += '<div style="margin-top:10px;width:auto;'+suf+'" class="medalbox"><h3>'+str(title)+'</h3><p>'+str(desc)+'</p></div>'
            html += '</div>'
            html += '<div class="cardcontainer spacetop spacebottom">'
            html += '<div class="title">Best Scores</div>'
            html += get_userscore(user=user,recent=False,mini=True,limit=10)
            html += '</div>'


            html += '<div class="cardcontainer spacetop">'
            html += '<div class="title">Last Played</div>'
            html += get_userscore(user=user,recent=True,mini=True,limit=10)
            html += '</div>'
        elif usertest[1]:
            html += '<div class="info"><span class="center"><h1>o-o</h1><h3>This profile has been privated QnQ</h3></span></div>'
        else:
            html += '<div class="info"><span class="center"><h1>o-o</h1><h3>The page you are looking for is not found or gotten sucked from a black hole...</h3></span></div>'
    tickle = round((time.time() - tickle) / 0.001,2)
    html += str(tickle)
    return HttpResponse(html)


def base(request, uri):
    if uri == "":
        return HttpResponse(header(request) + open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/home.html").read())
    elif uri == "download":
        return HttpResponse(header(request) + open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/download.html").read())
    elif uri == "ranking":
        htmltemp = header(request) + open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/ranking.html").read()
        html = ''
        users, tols = getstat('ranking', None, page=1)
        
        if not tols:
            html += "<h3 class='bar'>Someone needs to play more! (｡•̀ᴖ•́｡)</h3>"
        else:
            html += "<table class='tablebar'><tr><th>Rank</th><th>Username</th><th>Points</th><th>Score</th><th>Accuracy</th><th>MAX</th><th>GREAT</th><th>MEH</th><th>BAD</th></tr>"
            rank = 0
            
        for user in users:
            rank += 1
            points = user.ranked_points if user.ranked_points is not None else 0
            score = user.ranked_score if user.ranked_score is not None else 0
            acc = user.accuracy if user.accuracy is not None else 0
            max_hit = user.max if user.max is not None else 0
            great = user.great if user.great is not None else 0
            meh = user.meh if user.meh is not None else 0
            bad = user.bad if user.bad is not None else 0

            html += f"<tr><td class='lbar'>#{rank}</td>"
            html += f"<td class='cbar'><a href='/user/{user.username}'>{urllib.parse.unquote(user.username)}</a></td>"
            html += f"<td class='cbar'>{points:,}</td>"
            html += f"<td class='cbar'>{score:,}</td>"
            html += f"<td class='cbar'>{acc}%</td>"
            html += f"<td class='cbar'>{max_hit:,}</td>"
            html += f"<td class='cbar'>{great:,}</td>"
            html += f"<td class='cbar'>{meh:,}</td>"
            html += f"<td class='ebar'>{bad:,}</td></tr>"

                    
        html += "</table>"
        for a in range(1, 11):
            html += f"<a href='../ranking/{a}'><button class='minibutton'>{a}</button></a> "
        
        html += "</div></div><br>"
        htmltemp = htmltemp.replace('{entry}',html)
        return HttpResponse(htmltemp)