from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ThisMyPassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "5733664363"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(550))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
@app.before_request
def require_login():
    allowed_routes = ["login", "signup","blog"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route("/blog", methods = ["POST","GET"])
def blog():
    blog_title= Blog.query.all()
    print(blog_title)
    blog = ""
    
    id = request.args.get("id")
    user_id = request.args.get("user")
    if user_id:
        blog = Blog.query.filter_by(owner_id=user_id).all()
        
        return render_template("single_user.html",blog=blog)
    
    if id:
        blog = Blog.query.filter_by(id=id).all() 
        single_blog = blog[0]
        author = single_blog.owner
        user_id = str(request.args.get("user"))
        
        return render_template("single-post.html", blog=blog, author=author)

    

    return render_template("blog.html", blog_title=blog_title)

@app.route("/add-new-post", methods = ["POST", "GET"])
def blog_entry():
    error = ""
    owner = User.query.filter_by(username = session["username"]).first()
    if request.method == "POST":
         title = request.form["title"]
         body = request.form["body"]
         id = ""
    
         if not title or not body:
             error = "You may not leave any fields blank."
             return render_template("add-new-post.html", error=error)
         elif title and body:
             new_entry = Blog(title,body,owner)
             db.session.add(new_entry)
             db.session.commit()
             blog_id = str(new_entry.id)
             user_id = str(new_entry.owner_id)
             
             url = "/blog?id=" + blog_id 
           
             return redirect(url)
    return render_template("add-new-post.html")
@app.route("/signup", methods = ["POST", "GET"])
def signup():

    username = ""
    space = " "
    username_error = ""
    password_error = ""
    password = ""
    password_two = ""



    if request.method == "POST":
        password = str(request.form['password'])
        password_two = str(request.form['password2'])
        username = str(request.form["username"])
        existing_user = User.query.filter_by(username = username).first()
        
    
    
     
        username_error_flag = True
        password_error_flag = True
        
        

        
        if not username:
            username_error = " username field may not be left blank."
            username = ""
        elif len(username) > 20 or len(username) < 3:
            username_error = " username must be between 3 and 20 characters."
            username = ""
        elif space in username:
            username_error = "username may not contain any spaces."
            username = ""
        else:
            username_error_flag = False

        
        
        if len(password) > 26 or len(password) < 3:
            
            password_error = " password must be between 3 and 20 characters. "
        elif space in password:
            password_error= " password may not contain any spaces."
        elif password != password_two:
            password_error = " passwords do not match."
        else:
            password_error_flag = False

        if existing_user:
            username_error = "This username already exists"
        if not existing_user and not password_error_flag and not username_error_flag:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/add-new-post")
        
        


    return render_template("signup.html",username_error = username_error, 
    password_error = password_error, username = username)



@app.route("/login", methods = ["POST", "GET"])
def login():
    username_error = ""
    password_error = ""
    username = ""
    password = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            username_error = "username does not exist"
        elif password != user.password:
            password_error = "incorrect password"
        elif user and user.password == password:
            session["username"] = username
            return redirect("/add-new-post")
    return render_template("login.html", username_error = username_error,
    password_error = password_error, username = username)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/blog")


@app.route("/")
def index():
    blog = User.query.all()
    user_id = request.args.get("user")
    
    if user_id:
        return render_template("single_user.html",blog=blog)


        
    return render_template("index.html", blog = blog)  














if __name__ == '__main__':
    app.run()