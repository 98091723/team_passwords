import os
import sqlite3
import secrets
import string
import bleach
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, abort, g
)
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

# --- Flask & CSRF ---
app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
csrf = CSRFProtect(app)

# --- 数据库操作 ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

def init_db():
    db = get_db()
    db.executescript(open(os.path.join(os.path.dirname(__file__), 'schema.sql'), encoding='utf-8').read())
    db.commit()

if not os.path.exists(app.config['DATABASE']):
    with app.app_context():
        init_db()

# --- 安全工具 ---
def gen_team_key():
    return Fernet.generate_key()

def encrypt(value, key):
    return Fernet(key).encrypt(value.encode()).decode()

def decrypt(token, key):
    return Fernet(key).decrypt(token.encode()).decode()

def clean(s):
    return bleach.clean(s, tags=[], strip=True)

def audit_log(user_id, action, resource, resource_id, success, detail=None):
    db = get_db()
    db.execute(
        '''INSERT INTO audit_log (user_id, action, resource, resource_id, ip, user_agent, success, detail, created_at) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, action, resource, resource_id,
         request.remote_addr, request.headers.get('User-Agent', '')[:200], int(success), detail, datetime.utcnow())
    )
    db.commit()

# --- 权限校验 ---
def login_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*a, **kw)
    return wrap

# ---- Flask-WTF 表单 ----
class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])

class TeamForm(FlaskForm):
    name = StringField('团队名称', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('简介', validators=[Length(max=200)])

class EntryForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(min=1, max=50)])
    username = StringField('登录名', validators=[Length(max=50)])
    password = StringField('密码', validators=[Length(max=128)])
    website = StringField('网址', validators=[Length(max=100)])
    notes = TextAreaField('备注', validators=[Length(max=200)])

# --- 路由 ---
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db = get_db()
        username = clean(form.username.data)
        password = form.password.data
        try:
            db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('用户名已存在', 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = get_db()
        username = clean(form.username.data)
        password = form.password.data
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            flash('登录成功', 'success')
            audit_log(user['id'], 'login', 'user', user['id'], True)
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    user_id = session.get('user_id')
    audit_log(user_id, 'logout', 'user', user_id, True)
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    user_id = session['user_id']
    teams = db.execute(
        '''SELECT t.id, t.name, t.description, tm.role
           FROM teams t
           JOIN team_members tm ON t.id=tm.team_id
           WHERE tm.user_id=?''', (user_id,)
    ).fetchall()
    return render_template('dashboard.html', teams=teams)

@app.route('/team/create', methods=['GET','POST'])
@login_required
def team_create():
    form = TeamForm()
    if form.validate_on_submit():
        db = get_db()
        name = clean(form.name.data)
        desc = clean(form.description.data)
        key = gen_team_key()
        db.execute('INSERT INTO teams (name, description, team_key, owner_id) VALUES (?,?,?,?)',
                   (name, desc, key.decode(), session['user_id']))
        team_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.execute('INSERT INTO team_members (team_id, user_id, role) VALUES (?, ?, ?)',
                   (team_id, session['user_id'], 'owner'))
        db.commit()
        audit_log(session['user_id'], 'create_team', 'team', team_id, True)
        flash('团队创建成功', 'success')
        return redirect(url_for('dashboard'))
    return render_template('team_create.html', form=form)

@app.route('/team/<int:team_id>')
@login_required
def team_detail(team_id):
    db = get_db()
    team = db.execute('SELECT * FROM teams WHERE id=?', (team_id,)).fetchone()
    if not team:
        abort(404)
    member = db.execute('SELECT * FROM team_members WHERE team_id=? AND user_id=?',
                        (team_id, session['user_id'])).fetchone()
    if not member:
        abort(403)
    members = db.execute(
        '''SELECT u.username, tm.role FROM team_members tm 
           JOIN users u ON tm.user_id=u.id WHERE tm.team_id=?''', (team_id,)).fetchall()
    entries = db.execute(
        '''SELECT id, title, username, website FROM password_entries WHERE team_id=?''', (team_id,)).fetchall()
    role = member['role']
    return render_template('team_detail.html', team=team, members=members, entries=entries, role=role)

@app.route('/team/<int:team_id>/entry/create', methods=['GET','POST'])
@login_required
def entry_create(team_id):
    db = get_db()
    team = db.execute('SELECT * FROM teams WHERE id=?', (team_id,)).fetchone()
    if not team:
        abort(404)
    member = db.execute('SELECT * FROM team_members WHERE team_id=? AND user_id=?',
                        (team_id, session['user_id'])).fetchone()
    if not member:
        abort(403)
    form = EntryForm()
    if form.validate_on_submit():
        key = team['team_key'].encode()
        db.execute(
            '''INSERT INTO password_entries 
                (team_id, title, username, password, website, notes, created_by)
               VALUES (?,?,?,?,?,?,?)''',
            (team_id, 
             clean(form.title.data),
             encrypt(form.username.data or '', key),
             encrypt(form.password.data or '', key),
             clean(form.website.data or ''), 
             clean(form.notes.data or ''), 
             session['user_id'])
        )
        db.commit()
        audit_log(session['user_id'], 'create_entry', 'entry', team_id, True)
        flash('密码条目添加成功', 'success')
        return redirect(url_for('team_detail', team_id=team_id))
    return render_template('entry_create.html', form=form, team=team)

@app.route('/team/<int:team_id>/entry/<int:entry_id>')
@login_required
def entry_view(team_id, entry_id):
    db = get_db()
    team = db.execute('SELECT * FROM teams WHERE id=?', (team_id,)).fetchone()
    if not team:
        abort(404)
    member = db.execute('SELECT * FROM team_members WHERE team_id=? AND user_id=?',
                        (team_id, session['user_id'])).fetchone()
    if not member:
        abort(403)
    entry = db.execute('SELECT * FROM password_entries WHERE id=? AND team_id=?',
                       (entry_id, team_id)).fetchone()
    if not entry:
        abort(404)
    key = team['team_key'].encode()
    entry_data = {
        'title': entry['title'],
        'username': decrypt(entry['username'], key) if entry['username'] else '',
        'password': decrypt(entry['password'], key) if entry['password'] else '',
        'website': entry['website'],
        'notes': entry['notes']
    }
    return render_template('entry_view.html', entry=entry_data)

# 可继续补充 entry_edit, entry_delete, 成员管理等路由（与前文类似）

# --- 错误和安全响应头 ---
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message="无权限访问"), 403

@app.errorhandler(404)
def notfound(e):
    return render_template('error.html', error_code=404, error_message="未找到内容"), 404

@app.after_request
def set_headers(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    resp.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "font-src 'self' https://cdn.jsdelivr.net; img-src 'self' data:;"
    )
    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return resp

if __name__ == '__main__':
    app.run(debug=True)
    app.config['SECRET_KEY'] = '%aaNdQYB3Xz:at6'
    