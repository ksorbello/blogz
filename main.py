from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:LaunchCode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(550))


    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog", methods = ["POST","GET"])
def blog():
    blog_title= Blog.query.all()
    id = request.args.get("id")
    blog = ""
    if id:
        blog = Blog.query.filter_by(id=id).all()
        
        return render_template("single-post.html", blog=blog)

    

    return render_template("blog.html", blog_title=blog_title)#, blog_body=blog_body )

@app.route("/add-new-post", methods = ["POST", "GET"])
def blog_entry():
    error = ""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        id = ""
    
        if not title or not body:
            error = "You may not leave any fields blank."
            return render_template("add-new-post.html", error=error)
        elif title and body:
            new_entry = Blog(title,body)
            db.session.add(new_entry)
            db.session.commit()
            blog_id = str(new_entry.id)
            url = "/blog?id=" + blog_id
            #title = Blog.query.filter_by(title=title).first()
            #body = Blog.query.filter_by(body=body).first()
             
            # blog_one = Blog.query.filter_by(id=id).all()

   
            return redirect(url)
        
        

        

    return render_template("add-new-post.html")  














if __name__ == '__main__':
    app.run()