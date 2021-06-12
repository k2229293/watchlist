from flask import Flask,render_template,request,flash,redirect,url_for
from flask_login import login_required, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
import os
import click
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,LoginManager,current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    def validate_password(self, password):
        return check_password_hash(self.password_hash,password)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

@app.cli.command()
@click.option('--drop', is_flag=True, help='create after drop')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('数据库初始化完成')

@app.cli.command()
@click.option("--username",prompt=True,help="the username used to login")
@click.option("--password",prompt=True,hide_input=True,confirmation_prompt=True,help="the password used to login")
def admin(username,password):
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo("updating user")
        user.username = username
        user.set_password(password)
    else:
        click.echo('creating user')
        user = User(username=username, name="Admin")
        user.set_password(password)
    db.session.commit()
    click.echo('Done')

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

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('无效登录')
            return redirect(url_for('login'))
        
        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('成功登录')
            return redirect(url_for('index'))
        
        flash('用户名或密码错误')
        return redirect(url_for('login'))
    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user

@app.route('/settings',methods=['GET',"POST"])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 60:
            flash('无效用户名')
            return redirect(url_for('settings'))
        current_user.name = name
        db.session.commit()
        flash('设置成功')
        return redirect(url_for('index'))
    return render_template('settings.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('再见')
    return redirect(url_for('index'))


@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) >4 or len(title)>60:
            flash("错误输入")
            return redirect(url_for('index'))
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('条目已添加')
        return redirect(url_for('index'))
    movies = Movie.query.all()
    return render_template("index.html",movies=movies)

@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash("错误输入")
            return redirect(url_for('edit',movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Intem updated')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))

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



