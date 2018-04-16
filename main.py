from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beproductive@127.0.0.1:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body



@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    posts = Blog.query.all()
    
    blog_id = request.args.get("id")

    if (blog_id):
        blog = Blog.query.filter_by(id=blog_id).all()
        return render_template('main_blog.html', posts=posts, id=blog)

    return render_template('main_blog.html',posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        new_title = request.form['new_title']
        new_blog = request.form['new_blog']
        
        if new_title == '':
            flash('Blog title is empty!', 'error')
        
        if new_blog == '':
            flash("Blog body is empty!", 'error')
            
        if new_blog == '' or new_title == '':    
            return render_template('new_post.html',new_title=new_title, new_blog=new_blog)
        
        if new_blog != '' and new_title != '':
            new_blog_post = Blog(new_title, new_blog)
            db.session.add(new_blog_post)
            db.session.commit()
            x = Blog.query.filter_by(title=new_title).all()
            blog_ids = x[0].id
            blog_url = "blog?id=" + str(blog_ids)
            return redirect(blog_url)

    posts = Blog.query.all()
    
    return render_template('new_post.html',posts=posts)


if __name__ == '__main__':
    app.run()