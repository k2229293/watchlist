from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
import os
import click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

@app.route('/')
def index():
    name = User.query.first()
    movies = Movie.query.all()
    return render_template("index.html",movies=movies)

@app.route('/usr/<name>')
def user(name):
    return "welcome~!%s"%name

@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html'),404

@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@app.cli.command()
def forge():
    db.create_all()
    name = "shen"
    movies = [
                {'title': 'My Neighbor Totoro', 'year': '1988'},
                {'title': 'Dead Poets Society', 'year': '1989'},
                {'title': 'A Perfect World', 'year': '1993'},
                {'title': 'Leon', 'year': '1994'},
                {'title': 'Mahjong', 'year': '1996'},
                {'title': 'Swallowtail Butterfly', 'year': '1996'},
                {'title': 'King of Comedy', 'year': '1999'},
                {'title': 'Devils on the Doorstep', 'year': '1999'},
                {'title': 'WALL-E', 'year': '2008'},
            ]
    usr = User(name=name)
    db.session.add(usr)
    for i in movies:
        movie = Movie(title=i["title"],year=i["year"])
        db.session.add(movie)
    db.session.commit()
    click.echo("Done")
