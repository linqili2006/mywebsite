from flask import render_template, flash, redirect, abort, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .models import Judge, Player
from functools import wraps
import md5

ADMIN = 'admin'

def check_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if g.user.name != ADMIN:
            abort(401)
        return func(*args, **kwargs)
    return decorated_view


@app.route('/index')
@login_required
def index():
    judge_id = g.user.id
    players = Player.query.filter_by(judge_id=judge_id)
    return render_template("index.html", 
            title = "Count", players = players)

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

@app.route('/addJudge', methods=['POST'])
@login_required
@check_admin
def addJudge():
    name = request.form.get('name') 
    passwd = request.form.get('passwd') 

    passwd = md5.md5(passwd).hexdigest()

    db.session.add(Judge(name=name, passwd=passwd))
    db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/addPlayer', methods=['POST'])
@login_required
@check_admin
def addPlayer():
    name = request.form.get('name') 
    phone = request.form.get('phone')

    db.session.add(Player(name=name, phone=phone, judge_id=-1))
    db.session.commit()
    
    return redirect(url_for('admin'))
