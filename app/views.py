from flask import render_template, flash, redirect, abort, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .models import Judge, Player
from sqlalchemy.exc import IntegrityError
from functools import wraps
import md5
import json
import datetime

ADMIN = 'admin'
DONE = 0
FAILED = 1
AVAIL = -1

def check_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if g.user.name != ADMIN:
            abort(401)
        return func(*args, **kwargs)
    return decorated_view

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    try:
        return Judge.query.get(int(id))
    except:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name') 
        passwd = request.form.get('passwd')

        passwd = md5.md5(passwd).hexdigest()
        judge = Judge.query.filter_by(name=name, passwd=passwd).first() 
        if judge:
            login_user(judge)
            if name == ADMIN:
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
    return render_template('login.html', title='Sign In')
                            
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@check_admin
def admin():
    judges = Judge.query.all()
    players = Player.query.all()
    
    return render_template('admin.html', judges=judges, players=players)

@app.route('/admin/judges', methods=['GET'])
@login_required
@check_admin
def judges():
    judges = Judge.query.order_by('id desc').all()
    ret = []
    for judge in judges:
        if judge.name == ADMIN:
            continue
        ret.append({
            'id':judge.id,
            'name':judge.name,
            'createDate':datetime.datetime.strftime(judge.createDate, '%Y/%m/%d %H:%M:%S'),
            'comment':judge.comment,
        })
    return json.dumps(ret)

@app.route('/admin/addJudge', methods=['POST'])
@login_required
@check_admin
def addJudge():
    name = request.form.get('name') 
    passwd = request.form.get('passwd') 
    comment = request.form.get('comment') 

    passwd = md5.md5(passwd).hexdigest()

    createDate = datetime.datetime.now()

    ret = {'code':DONE}
    try:
        db.session.add(Judge(name=name, passwd=passwd, 
                             comment=comment, createDate=createDate))
        db.session.commit()
    except IntegrityError:
        ret['code'] = FAILED
        ret['message'] = "judge %s is already existed" % name
    except Exception, e:
        ret['code'] = FAILED
        ret['message'] = "add judge failed"

    return json.dumps(ret)

@app.route('/admin/delJudge', methods=['POST'])
@login_required
@check_admin
def delJudge():
    judge_id = request.form.get('id') 

    judge = Judge.query.filter_by(id=judge_id).first()
    players = Player.query.filter_by(judge_id=judge_id)
    ret = {'code':DONE}
    try:
        if judge:
            for player in players:
                player.judge_id = AVAIL
            db.session.delete(judge)
            db.session.commit()
    except Exception, e:
        ret['code'] = FAILED
        ret['message'] = "delete judge failed"

    return json.dumps(ret)

@app.route('/admin/players', methods=['GET'])
@login_required
@check_admin
def adminPlayers():
    players = Player.query.order_by('id desc').all()
    ret = []
    for player in players:
        ret.append({
            'id':player.id,
            'name':player.name,
            'phone':player.phone,
            'score':player.score,
            'createDate':datetime.datetime.strftime(player.createDate, '%Y/%m/%d %H:%M:%S'),
            'comment':player.comment,
        })
    return json.dumps(ret)

@app.route('/admin/clearScoreOfAllPlayers', methods=['POST'])
@login_required
@check_admin
def clearScoreOfAllPlayers():

    ret = {'code':DONE}
    try:
        players = Player.query.all()
        for player in players:
            player.score = 0
        db.session.commit()
    except Exception, e:
        ret['code'] = FAILED
        ret['message'] = "clear score failed"
    return json.dumps(ret)
    
    
@app.route('/admin/addPlayer', methods=['POST'])
@login_required
@check_admin
def addPlayer():
    name = request.form.get('name') 
    phone = request.form.get('phone') 
    comment = request.form.get('comment') 

    createDate = datetime.datetime.now()

    ret = {'code':DONE}
    try:
        db.session.add(Player(name=name, phone=phone, 
                              judge_id=AVAIL, score=0, 
                              comment=comment, createDate=createDate))
        db.session.commit()
    except IntegrityError:
        ret['code'] = FAILED
        ret['message'] = "phone number %s is already existed" % phone
    except Exception, e:
        ret['code'] = FAILED
        ret['message'] = "add player failed"

    return json.dumps(ret)

@app.route('/admin/editPlayer', methods=['POST'])
@login_required
@check_admin
def editPlayer():
    player_id = request.form.get('id') 
    name = request.form.get('name') 
    phone = request.form.get('phone') 
    comment = request.form.get('comment') 

    ret = {'code':DONE}
    try:
        player = Player.query.filter_by(id=player_id).first()
        if player:
            player.name = name
            player.phone = phone
            player.comment = comment
            db.session.commit()
    except IntegrityError:
        ret['code'] = FAILED
        ret['message'] = "phone number %s is already existed" % phone
    except Exception, e:
        ret['code'] = FAILED
        ret['message'] = "update player failed"

    return json.dumps(ret)

@app.route('/admin/delPlayer', methods=['POST'])
@login_required
@check_admin
def delPlayer():
    player_id = request.form.get('id') 

    player = Player.query.filter_by(id=player_id).first()
    ret = {'code':DONE}
    try:
        if player:
            db.session.delete(player)
            db.session.commit()
    except Exception, e:
        ret['code'] = FAILED
        ret['message'] = "delete player failed"

    return json.dumps(ret)

@app.route('/index')
@login_required
def index():
    return render_template("index.html")

@app.route('/players', methods=["GET"])
@login_required
def players():
    ret = []
    ranking = 1
    try:
        players = Player.query.order_by("score desc").all()
        for player in players:
            ret.append({
                'id':player.id,
                'ranking':ranking,
                'name':player.name,
                'phone':player.phone,
                'score':player.score,
                'comment':player.comment,
            })
            ranking += 1
    except Exception,e:
        print str(e)

    return json.dumps(ret)

@app.route('/judge/players')
@login_required
def judgePlayers():
    judge_id = g.user.id

    ret = []
    ranking = 1
    try:
        players = Player.query.filter_by(judge_id=judge_id).order_by("score desc")
        for player in players:
            ret.append({
                'id':player.id,
                'ranking':ranking,
                'name':player.name,
                'phone':player.phone,
                'score':player.score,
                'comment':player.comment,
            })
            ranking += 1
    except Exception,e:
        print str(e)

    return json.dumps(ret)

@app.route('/judge/availPlayers')
@login_required
def availPlayers():
    players = Player.query.filter_by(judge_id=AVAIL)
    ret = []
    for player in players:
        ret.append({
            'id':player.id,
            'name':player.name,
            'phone':player.phone,
            'score':player.score,
            'comment':player.comment,
        })
    return json.dumps(ret)

@app.route('/judge/addPlayerToGame', methods=["POST"])
@login_required
def addPlayerToGame():
    ids = request.form.get('ids')

    ret = {'code':DONE}
    try:
        ids = ids.split(',')
        for player_id in ids:
            player = Player.query.filter_by(id=player_id).first()
            if player:
                if player.judge_id != AVAIL:
                    raise Exception('player %s is busy now' % player.name)
                player.judge_id = g.user.id
        db.session.commit()
    except Exception,e:
        ret['code'] = FAILED
        ret['message'] = str(e)

    return json.dumps(ret)

@app.route('/judge/delPlayerFromGame', methods=["POST"])
@login_required
def delPlayerFromGame():
    player_id = request.form.get('id')
    deleteAll = request.form.get('deleteAll')

    judge_id = g.user.id
    ret = {'code':DONE}
    print player_id
    try:
        if deleteAll is not None and int(deleteAll):
            players = Player.query.filter_by(judge_id=judge_id)
            for player in players:
                player.judge_id = AVAIL
        elif player_id is not None:
            player = Player.query.filter_by(id=player_id).first()
            if player:
                player.judge_id = AVAIL
            else:
                raise Exception("player %s is not existed" % player_id)
        db.session.commit()
    except Exception,e:
        ret['code'] = FAILED
        ret['message'] = str(e)

    return json.dumps(ret)

@app.route('/judge/updateScore', methods=["POST"])
@login_required
def updateScore():
    id = request.form.get('id')
    score = request.form.get('score')

    ret = {'code':DONE}
    try:
        player = Player.query.filter_by(id=id).first()
        if player:
            player.score = score
            db.session.commit()
    except Exception,e:
        ret['code'] = FAILED
        ret['message'] = str(e)

    return json.dumps(ret)
