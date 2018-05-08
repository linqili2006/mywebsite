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
        if g.user is not None and g.user.is_authenticated:
            if g.user.name == 'admin':
                return redirect(url_for('admin'))
            return redirect(request.args.get('next') or url_for('index'))

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

@app.route('/admin/judgeList', methods=['GET'])
@login_required
@check_admin
def judgeList():
    judges = Judge.query.order_by('-id').all()
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
    ret = {'code':DONE}
    try:
        if judge:
            db.session.delete(judge)
            db.session.commit()
    except Exception, e:
        ret['code'] = FAILED
        ret['message'] = "delete judge failed"

    return json.dumps(ret)

@app.route('/admin/playerList', methods=['GET'])
@login_required
@check_admin
def playerList():
    players = Player.query.order_by('-id').all()
    ret = []
    for player in players:
        ret.append({
            'id':player.id,
            'name':player.name,
            'phone':player.phone,
            'createDate':datetime.datetime.strftime(player.createDate, '%Y/%m/%d %H:%M:%S'),
            'comment':player.comment,
        })
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
                              judge_id=-1, score=0, 
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

    print player_id, phone, comment
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
    judge_id = g.user.id
    players = Player.query.filter_by(judge_id=judge_id)
    return render_template("index.html", 
            title = "Count", players = players)

