# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

basedir = os.path.abspath(os.path.dirname(__file__))
# os.path.abspath(name):获得绝对路径,os.path.dirname(path):返回文件路径

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'data1.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# print 'sqlite:///' + os.path.join(basedir, 'data1.sqlite')

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('submit')
    password = PasswordField('password')
    
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')
    
    def __repr__(self):
        return '<Role %r>' % self.name
        
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
        
    def __repr__(self):
        return '<User %r>' % self.username 

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit(): # Required function decide it's value
        usr = User.query.filter_by(username=form.name.data).first()
        if usr is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['know'] = False
        else:
            session['know'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                            know=session.get('know', False),
                            current_time=datetime.utcnow())
  
   
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
    
if __name__ == '__main__':
    db.create_all()
    manager.run()