from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@127.0.0.1:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    content = db.Column(db.String(1000))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author


@app.before_request
def require_login():
    allowed_routes = ['login', 'sign_up', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST','GET'])
def index():
    usernames = User.query.all()
    return render_template('index.html', username=usernames)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    posts = Blog.query.all()
    blog_id = request.args.get("id")
    username = request.args.get("user")

    if (blog_id):
        blog = Blog.query.filter_by(id=blog_id).all()
        return render_template('main_blog.html', posts=posts, id=blog)
    elif (username):
        user = User.query.filter_by(username=username).first()
        user_id = user.id
        author_blogs = Blog.query.filter_by(author_id=user.id).all()

        return render_template('singleUser.html', id=author_blogs,username=username)

    return render_template('main_blog.html',posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    #got to get the author id working
    author = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        new_title = request.form['new_title']
        content = request.form['new_blog']
        
        if new_title == '':
            flash('Blog title is empty!', 'error')
        
        if content == '':
            flash("Blog body is empty!", 'error')
            
        if content == '' or new_title == '':    
            
            return render_template('new_post.html',new_title=new_title, content=content)
        
        if content != '' and new_title != '':
            content_post = Blog(new_title, content, author)
            db.session.add(content_post)
            db.session.commit()
            x = Blog.query.filter_by(title=new_title).all()
            blog_ids = x[0].id
            blog_url = "blog?id=" + str(blog_ids)
            return redirect(blog_url)

    posts = Blog.query.all()
    
    return render_template('new_post.html',posts=posts)

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if username == '':
            flash('Please enter a username', 'error')
        
        if password == '':
            flash('Please enter a password', 'error')

        if username == '' or password == '':
            return render_template('login.html', username=username)

        if user == None:
            flash('username is incorrect, or does not exist', 'error')
            return render_template('login.html', username=username)
            
        if user and user.password == password:
            session['username'] = username
            flash('Logged in!')
            return redirect('/newpost')
        else:
            flash('user password incorrect, or user does not exist', 'error')
            return render_template('login.html', username=username)

    return render_template('login.html')

@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '':
            flash('Please enter a username', 'error')
        elif len(username) < 3:
            flash('Please enter a valid username that is longer then 3 characters', 'error')

        if password == '':
            flash('Please enter a password', 'error')
        elif len(password) < 3:
            flash('Please enter a valid password that is longer then 3 characters', 'error')

        if verify == '':
            flash('Please verify password', 'error')
        
        if password != verify:
            flash('Please enter matching passwords', 'error')
            return render_template('sign_up.html', username=username)

        if username == '' or password == '' or verify == '':
            return render_template('sign_up.html', username=username)

        if len(username) < 3 or len(password) < 3:
            return render_template('sign_up.html', username=username)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('username already is already taken, please enter a new username', 'error')
            return render_template('sign_up.html', username=username)

    return render_template('sign_up.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('Logged out')
    return redirect('/blog')

if __name__ == '__main__':
    app.run()