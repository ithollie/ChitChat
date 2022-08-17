from flask import Flask, render_template, escape, make_response, redirect,session, request,jsonify,json, flash,url_for
from flask import Flask,redirect,url_for,session,render_template,request,flash,make_response
from sendemail.registration_email_sender.registeration_email_sender import Regmail
import ssl
import sys
import os
import re
import uuid
import logging 
import datetime
import socket, ssl

from  hashlib import md5
from  common.database import Database
from  models import constants as UserConstants
from  models.System_file import File_system
from  common.Utils import utils

from models.user.User import Users
from werkzeug.utils import secure_filename

from werkzeug.datastructures import  FileStorage
from models.flask_wtf.register import RegisterForm
from RegisterForm.RegisterForm import RegForm as Form

from models.user import error as UserErrors
from bson.objectid import ObjectId

#from models.comments.comment import Comments
#from models.flask_wtf.login import LoginForm
#from models.flask_wtf.blogform import BlogForm
# from models.flask_wtf.editeform import EditeForm
# from models.flask_wtf.commentform import CommentForm


context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = False
context.load_default_certs()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_sock = context.wrap_socket(s, server_hostname='www.verisign.com')
ssl_sock.connect(('www.verisign.com', 443))


app = Flask(__name__)
UPLOAD_FOLDER = os.path.basename('static') + "/uploads"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = os.urandom(24)

@app.before_first_request
def initialize_database():
    Database.initialize()
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')
    
@app.route('/')
def route():
    session.pop('login_email', None)
    response = make_response(redirect(url_for('desk')))
    response.set_cookie('login_email', "")
    response.set_cookie('login_author', "")
    response.set_cookie('login_id', "")
    return  response

@app.route('/admin_login')
def admin_login():
    return  render_template('admin.html')

#payment
@app.route('/payments')
def  payment():
    return   render_template('checkout.html')

@app.route('/create_payment', methods=['POST'])
def create_payment():
    # Set your secret key. Remember to switch to your live secret key in production!
    # See your keys here: https://dashboard.stripe.com/account/apikeys
    stripe.api_key = 'sk_test_51GwtgkIQPsh84HxzSuwteCTaIP6GLOpApnk1REv2i3zZJlLVONUURoIrdvcwFdr0t8kdj0TpHGEjjRj9qgC3XMgf004VS3DWOs'

    intent = stripe.PaymentIntent.create(
    amount=1099,
    currency='usd',
    # Verify your integration in this guide by including this parameter
    metadata={'integration_check': 'accept_a_payment'},
    )
#secret
@app.route('/secret')
def secret():
  return jsonify(client_secret=intent.client_secret)


@app.route('/activate')
def activate():
    return render_template('activate.html')
    
app.route('/signUpUser', methods=['POST'])
def signUpUser():
    user =  request.form['username']
    password = request.form['password']
    return json.dumps({'status':'OK','user':user,'pass':password})
    

@app.route('/blogs/current_user/<string:email>/<string:_id>')
def allblog(email,_id):
    if utils.email_is_valid(email) ==  True and 'user' in session and session['login_email'] == email:
        ids = Users.id_one_user(_id)['_id']
        blog_id =  Users.get_by_email(email)['_id']
        dataemail = Users.bgemail_one(request.cookies.get('login_email'))
        dataemail = Users.get_by_email(session['user'])['email']
        if email ==  dataemail:
            return redirect(url_for('memebership',email=dataemail,_id=_id))
        else:
            flash("not good")
            render_template('page_not_found.html')
    return render_template('page_not_found.html')

@app.route('/memebers/<string:email>/<string:_id>')
def memebership(email,_id):
    loginform = LoginForm()
    cookie_email = request.cookies.get('email')
    blogs = Database.find("blogs",{"email": { "$nin":[cookie_email]} })
    if 'user' in session and  cookie_email == email:
        return render_template("maini.html", blogs=blogs)
    else:
        return render_template("login.html" , loginform=loginform)

@app.route('/likes' , methods=['POST', 'GET'])
def likes():
    loginform = LoginForm()
    title = request.get_json()['title']
    email = request.get_json()['email']
    _id =   request.get_json()['_id']
    
    current_clikes =   request.get_json()['current_num']
    print(title)
    print(email)
    print(_id)
    print(current_clikes)
    if  request.method == "POST":
        if utils.email_is_valid(email) == True and  Users.likes("blogs",_id, title)["likes"] < int(current_clikes):
            likes = Users.likes("blogs",_id, title)["likes"]
            thuplikes(current_clikes,_id, title)
            return render_template("error.html")
        else:
            return redirect(url_for('login_route'))
    return redirect(url_for('login_route'))

# dislike route function
@app.route('/dislikes' , methods=['POST', 'GET'])
def dislikes():
    loginform = LoginForm()
    title = request.get_json()['title']
    email = request.get_json()['email']
    _id =   request.get_json()['_id']
    
    current_clikes =   request.get_json()['current_num']
    print(title)
    print(email)
    print(_id)
    print(current_clikes)
    if  request.method == "POST":
        if utils.email_is_valid(email) == True and Users.dislikes("blogs",_id,  title)['dislikes'] < int(current_clikes):
            likes = Users.dislikes("blogs", _id, title)["dislikes"]
            thupdislikes(current_clikes,_id, title)
            return render_template("error.html")
        else:
            return redirect(url_for('login_route'))
    return redirect(url_for('login_route'))
# dislike function
def thupdislikes(dislikes=None,blog_id=None, title=None):
        if dislikes is not None:
            Database.updates("blogs",{"title":title},{"$set": {"dislikes":dislikes}})
#likes function
def thuplikes(likes=None,blog_id=None, title=None):
        if likes is not None:
            Database.updates("blogs",{"title":title},{"$set": {"likes":likes}})
               
def check_likes(user,blogtitle):
        data = Database.find_one(user,{"title":blogtitle})
        if data['title'] == blogtitle:
            return data['likes']
            
def insert_likes(email,number, title):
        Database.updates("blogs",{"title":title},{"$addToSet": {"likes":number}})

@app.route('/thumbdown/<string:blogtitle>/<string:email>/<string:blog_id>')
def thumbdown(email,blogtitle,blog_id):
    loginform = LoginForm()
    if  'user' in session and blog_id.__len__() ==  32:
        ids = Users.id_one(blog_id)['_id']
        if utils.email_is_valid(email) == True and blog_id == ids:
            dislikes = Users.querytitlei(blogtitle)['dislikes']
            thdow(int(dislikes),blogtitle,blog_id)
            return render_template("dislikes.html")
        else:
            return redirect(url_for('login_route'))
    return redirect(url_for('login_route'))

def thdow(dislikes,blogtitle,blog_id):
    check_email = session['user']
    user = "user"
    user_dislikes = check_dislikes(user,check_email,blogtitle,blog_id)
    if user_dislikes !=  blogtitle:
        dislikes = dislikes + 1
        insert_dislikes(session['user'],blogtitle)
        Database.updates("blogs",{"_id":blog_id},{"$set": {"dislikes":dislikes}})
    else:
        return False

def check_dislikes(user,check_email,blogtitle,blog_id):
        data = Database.find_one(user,{"email":check_email})
        for items in data['dislikes']:
            return items
def insert_dislikes(email,titleblog):
        Database.updates("user",{"email":email},{"$addToSet": {"dislikes":titleblog}})

@app.route('/create/blog')
def create_blog():
    message = "You  are not a valiable user"
    if request.cookies.get('login_email') is not None:
	       return render_template('blogform.html')
    else:
        return redirect(url_for('login_route',message=message))
        
@app.route('/user/blogs')
def userBlogs():
    message = "You  are not a logined user  please login"
    if request.cookies.get('login_email') is  not None:
        return redirect(url_for('asset'))
    return redirect(url_for('login_route', message=message))
    
    
@app.route('/blogs')
def asset():
    if  request.cookies.get('login_email') is not None:
        email  = request.cookies.get('login_email')
        data =  Database.find_one(UserConstants.COLLECTION,{'email':email})
        blogs  = Database.find("blogs", {'email':email})
        return render_template('userblog.html', author=data['firstname'], lastname=data['lastname'], email=request.form['email'], blogs=blogs,  date = datetime.datetime.utcnow())

@app.route('/open/<string:email>/<string:blogtitle>/<string:blog_id>')
def open(email,blogtitle,blog_id):
        if utils.email_is_valid(email) == True and blog_id.__len__() ==  32:
            item = Users.bytitle_one(blogtitle)
            ids = Users.id_one(blog_id)["_id"]
            if  session['user'] == email and ids == blog_id:
                items =  Users.bytitle(blogtitle)
                return render_template('blogopen.html',items=items)
            else:
                flash("there is a problem contact Admin")
                return redirect(url_for('login_route'))
        flash("there is a problem please contact admin")
        return redirect(url_for('login_route'))
@app.route('/edite/blog/<string:email>/<string:titleblog>/<string:blog_id>')
def edite(email,titleblog,blog_id):
    properties = []
    editeform = EditeForm()
    loginform = LoginForm()

    if 'user' in session and session['user'] == email and blog_id and utils.email_is_valid(email) == True and blog_id.__len__() ==  32:
        data_id =       Users.get_by_email(email)["_id"]
        content = Users.bytitle(titleblog)
        for stuffs in content:
            ids = Users.id_one(blog_id)["_id"]
            if session['user'] == email and blog_id ==  ids:
                editeform.description.data = stuffs['content']
                return render_template('edite.html',editeform=editeform,email=email,blogtitle=titleblog,blog_id=blog_id)
            else:
                flash("checking problem")
                return redirect(url_for('login_route'))
    return redirect(url_for('login_route'))

@app.route('/editeprocess/<string:email>/<string:blogtitle>/<string:blog_id>', methods=('POST', 'GET'))
def editeprocess(email,blogtitle,blog_id):
    editeform = EditeForm()
    loginform = LoginForm()
    database_email = Users.get_by_email(email)["email"]
    if editeform.validate_on_submit() == True and 'user' in session and session['user'] == email and blog_id.__len__() ==  32:
        thins = Users.bytitle(blogtitle)
        ids = Users.id_one(blog_id)["_id"]
        for stuff in thins:
            if stuff['titleblog'] == blogtitle and stuff['email'] == session["user"] and blog_id == ids:
                description = editeform.description.data
                Database.updates("blogs",{"content":stuff['content']},{"$set": {"content":description}})
                return render_template('editemessage.html')
            else:
                redirect(url_for('login_route'))
    flash("these are technical errors please try login again")
    return render_template('login.html',loginform=loginform)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    loginform = LoginForm()
    
    post_title = request.get_json()['post_title']
    post_email = request.get_json()['post_email']
    post_id = request.get_json()['post_id']
    
    session['post_title']  = post_title
    session['post_email']  = post_email
    session['post_id']     = post_id
     
    if 'post_title' in  session:
        if post_id:
            print("that  is not quite")
            Database.delete("blogs",{"title":post_title})
            flash("blog deleted")
            return redirect(url_for('welcome'))
        else:
            print("that  is not quite corrent")
            return redirect(url_for('welcome'))
    print("that  is not quite yet")
    return redirect(url_for('welcome'))

@app.route('/comment/<string:blogtitle>/<string:email>/<string:blog_id>')
def commentUser(blogtitle,email,blog_id):
    commentform = CommentForm()
    if utils.email_is_valid(email) == True and 'user' in session and blog_id.__len__() ==  32:
        ids = Users.id_one(blog_id)["_id"]
        if email and blog_id ==  ids:
            commentform.title.data = blogtitle
            return render_template('comment.html',commentform=commentform)
        else:
            flash("check problem")
            return redirect(url_for('login_route'))
    flash('there is a problem with you information')
    return redirect(url_for('login_route'))


# comment rout
@app.route('/commentdetails/<string:email>/<string:blogtitle>/<string:blog_id>')
def commentdetails(blogtitle,email,blog_id):
    if blog_id.__len__() ==  32:
        ids = Users.id_one(blog_id)['_id']
        if blog_id == ids and ids != False:
            item = Users.bytitle_one(blogtitle)
            totalcomment = Users.allcomments(blogtitle)
            blogs =  Users.bytitle(blogtitle)
            return render_template('totalcomment.html',totalcomment=totalcomment,blogs=blogs)
        else:
            flash(" big problem ")
            return redirect(url_for('login_route'))
    flash("big problem man")
    return redirect(url_for('login_route'))

#comment been process and store in the database
@app.route('/commentor', methods=['POST', 'GET'])
def commentor():   
    login = request.cookies.get('login_email')
    if  request.method  == 'POST' and login is not None:
        
        #blog detils
        titleBlog = request.get_json()['blog_title']
        email = request.get_json()['blog_email']
        comment = request.get_json()['blog_comment']
        _id = request.get_json()['blog_id']
    
        #who commenting
        login_name = request.get_json()["_user"]
        login_email = request.get_json()['_email']
        login_id = request.get_json()['_id']
        
        commenter = {"name":login_name, "email":login_email,"_id":login_id}
        print("title"+" "+titleBlog)
        print(email)
        print(comment)
        print(_id)
        #set  comment detail  in  to the brower
        
        print("commenting user is _"+login_name)
        print("commenting email is _"+login_email)
        print("commenting id is _"+login_id)
        
        if Users.blogExists(titleBlog) == True:
            comment = Comments(titleBlog=titleBlog,comment=comment, email=email, _id=_id, commenter=commenter)
            comment.save_to_mongo(titleBlog)
            return ""
        else:
            print("something is going fine but what")
    return redirect(url_for('login_route'))

#comment been process and store in the database
@app.route('/saysomething', methods=['POST', 'GET'])
def saysomething():   
    login = request.cookies.get('login_email')
    saydata = Database.find(request.cookies.get('login_email')+"saycomment",{"login_email":request.cookies.get('login_email')})
    if  request.method  == 'POST' and login is not None:
        #user commenting
        login_name = request.get_json()["_user"]
        login_email = request.get_json()['_email']
        login_id = request.get_json()['_id']
        text     = request.get_json()['_text']
        
        commenter = {"name":login_name, "email":login_email,"_id":login_id,"text":text}
        if login_name != "":
            if saydata.count() == 0:
                Database.insert(login_email+"saycomment",
                        {"login_name":login_name,
                        "login_email":login_email,
                        "login_id":login_id ,
                        "likes":0,
                        "dislikes":0,
                        "text":text,
                        "comment":0})
              
                return redirect(url_for('welcome'))
            elif saydata.count() == 1:
                Database.updates(login_email+"saycomment",{"login_email":login_email},{"$set": {"text":text}})            
    return redirect(url_for('login_route'))
def number_title(comment,titleblog):
		comment = comment + 1
		Database.updates("blogs",{"titleblog":titleblog},{"$inc": {"comment":1}})
		
# this rout display blogs
@app.route('/allcomments/<string:titleblog>')
def details(titleblog):
    if titleblog ==  request.cookies.get('title') and 'user' in session:
        title = request.cookies.get('title')
        totalcomment = Users.allcomments(title)
        comment = Users.querytitlei(title)['comment']
        blogs =  Users.bytitle(title)
        number_title(comment,title)
        return render_template('totalcomment.html', totalcomment=totalcomment,blogs=blogs)
    return redirect(url_for('login_route'))

@app.route('/allcommentsofuser')
def detailsu(title):
    if 'user' in session and session['user'] == request.cookies.get('email'):
	    totalcomment = Users.allcomments(title)
	    blogs = Users.bytitle(title)
	    return render_template('totalcomment.html',totalcomment=totalcomment,blogs=blogs)
    else:
       return redirect(url_for('login_route'))

#image upload
@app.route('/upload/successfull',methods=['POST'])
def upload():
	path = os.getcwd()
	if request.method =='GET':
         filename = request.files['file']
         if filename is not None:
                     filename.save(path+secure_filename(filename.filename))

#image upload couple
@app.route('/imageupload',methods=['POST'])
def coupleImageUpload():
    path = os.getcwd()
    if request.method == 'POST':
        
            text = request.form['text']
            file = request.files['file']
        
            if file is not None and os.getcwd() +'/static/' is not None:
                current = os.getcwd() +'/static/'
                if os.listdir(current).__contains__("myboo") !=  True:
                    os.mkdir(current + "myboo")
                    Users.mybooInsert("myboo", file.filename,request.cookies.get('login_author'), request.cookies.get('login_email'), text)
                    print("complete thank you  are in the if")        
                    currentfile = secure_filename(file.filename)
                    print("User details"+request.cookies.get('login_author'), request.cookies.get('login_email'), currentfile)
                    file.save(os.path.join(os.getcwd()+ '/static/' +"myboo", currentfile))
                    return redirect(url_for('welcome'))
                elif os.listdir(current).__contains__("myboo") ==  True:
                    Users.mybooInsert("myboo", file.filename,request.cookies.get('login_author'), request.cookies.get('login_email'), text)
                    print("complete thank you elif")        
                    currentfile = secure_filename(file.filename)
                    print("User details"+request.cookies.get('login_author'), request.cookies.get('login_email'), currentfile)
                    file.save(os.path.join(os.getcwd() + '/static/' +"myboo", currentfile))
                    return redirect(url_for('welcome'))
                else:
                    print("you are here")
                    return redirect(url_for('welcome'))
            else:
                return redirect(url_for('login_route'))
    return redirect(url_for('welcome'))
    
    
#image uplaod  render 
@app.route('/imagecouple')
def  couple():
    if request.cookies.get('login_email') != "":
        return render_template('couple.html')
    else:
        return redirect(url_for('login_route'))
#blog creation rout
@app.route('/blogform')
def Blogform():
        num  = 0;
        blogform = BlogForm(request.cookies.get("login_author") ,None, request.cookies.get('login_email'), request.cookies.get('login_id'),None,None)
        if utils.email_is_valid(request.cookies.get('login_email')) == True:
            if request.cookies.get('login_email') != "" and blogform.author  == request.cookies.get('login_author'):
                return render_template('blogform.html', author=blogform.author, email=blogform.email)
            else:
                flash("things are bad")
                return redirect(url_for('login_route'))

        flash("not good")
        
        return redirect(url_for('login_route'))
        
#vid creation process
@app.route('/action', methods=['POST', 'GET'])
def video():
    if request.method == 'POST' and request.cookies.get('login_email') is  not  None:
      video  = request.form['video']
      Database.updates("user",{"email":request.cookies.get('login_email')},{"$set": {"youtube":video}})
      return  redirect(url_for('welcome'))
      #return render_template('uploadvideo.html',point="Thank  you for uploading a video")
    return redirect(url_for('login_route'))


#blog video process
@app.route('/video_actions', methods=['POST', 'GET'])
def clipvideo():
    dataImage = Database.find_one("user", {'email':request.cookies.get('login_email')})
    if request.method == 'POST' and request.cookies.get('login_email') is  not  None and dataImage is not None:
        name     = request.cookies.get('login_author')
        email    = request.cookies.get('login_email')
        filename = secure_filename(request.files['file'].filename)
        
        request.files['file'].save(os.path.join(os.getcwd() +'/static/uploads/videos', filename))
        data =  Database.find_one(UserConstants.COLLECTION,{"email":email})
        Database.insert("videos", {
            "username":name,
            "email":email,
            "image":dataImage['image'],
            "filename":filename
        })
        response = make_response(redirect(url_for('welcome')))
        response.set_cookie('login_email', email)
        response.set_cookie('login_author', data['firstname'])
        response.set_cookie('login_id', data['_id'])
        return response
        
    return redirect(url_for('login_route'))
#blog creation process
@app.route('/actions', methods=['POST', 'GET'])
def blog():
    blogform = BlogForm(request.form['author'], request.form['title'],request.form['email'],request.cookies.get('login_id'),request.form['description'], request.files['file'])

    if request.method == 'POST' and request.cookies.get('login_email') is  not  None:
        
        author  = blogform.author
        title =   blogform.title
        email =   blogform.email
        description = blogform.description
        titleblog =  title.lower()

        f = blogform.filename
        filename = secure_filename(f.filename)
        f.save(os.path.join(os.getcwd() +'/static/uploads', filename))
        
        print(Users.blogExists(request.form['title']))
    
        if Users.blogExists(request.form['title'])  == False:
            blogMailer = Blogmailer(email)
            blogMailer.send()
            print("post has been  uploaded and an email address has been sent")
            userImage =  Database.find_one("user", {"firstname":author})['image']
            cookie = request.cookies.get('login_email')
            person = Users.get_by_email(cookie)
            blog = Blogs(author=author,titleblog=titleblog,description=description,email=email,filename=filename, userImage=userImage)
            blog.save_to_mongo()
            if request.cookies.get('login_email') ==  email:
                data =  Database.find_one(UserConstants.COLLECTION,{"email":email})

                flash('you have successfull created a blog')
                response = make_response(redirect(url_for('welcome')))
                response.set_cookie('login_email', request.form['email'])
                response.set_cookie('login_author', data['firstname'])
                response.set_cookie('login_id', data['_id'])
                return response
            else:
                return render_template('blogform.html',point=blogform.message("A blog with that name already exist") )
        else:
            return render_template('blogform.html',point=blogform.message("A blog with that name already exist"))
    return redirect(url_for('login_route'))
    
@app.route('/help/blog')
def help():
	return render_template('create_blog.html')        
@app.route('/log')
def logno():
    return redirect(url_for('login_route'))


@app.route('/auth/restpass',methods=['POST','GET'])
def pass_rest():
	if request.method == 'POST':
		email = request.form['email']
		object_file = File_system()
		users_conn =  Restp(email)
		mal = users_conn.checkmliame(email)
		mailer = users_conn.checkmail(mal)

		image = object_file.image(request.form['email'])
		if mailer is not None:
			response = make_response(redirect(url_for('change_user', email=request.form.get('email'),id=image['_id'])))
			response.set_cookie('email',request.form.get('email'))
			return response
		else:
			print("Error message")
	return redirect(url_for('login_route'))

@app.route('/change_system_password/change_users_password/<string:email>/<id>')
def change_user(email,id):
	return render_template("edit_pass.html")

#acccount activation
@app.route('/active/account/')
def update_activation_status():
	url = "activate.html"
	routeUrl = Urls()
	return render_template(routeUrl.update_activation_status_url(url))

#prompt user to enter email and password
@app.route('/auth/account/activated/',methods=['POST','GET'])
def activated():
	User_utils = utils()
	loginform =  LoginForm()
	if request.method == 'POST':
		user_password = request.form['password']
		userEmail =  request.form['email']
		active = activate_account(userEmail)
		databaseEmail = active.getEmail(userEmail)
		if user_password and userEmail:

			active.Update(User_utils.check_hash_password(request.form['password'],databaseEmail['password']))
		else:
			return False
	flash("Thank you for activating you account")
	return render_template("login.html", loginform=loginform)

@app.route('/home')
def index():
    return render_template('index.html', search='Voodoo', email='ithollie@yahoo.com', login='true')

@app.route('/sign_in')
def sign():
    session['email'] = None
    return render_template('login.html')
    
@app.route('/changepassword')
def changePassword():
    return  render_template('changepassword.html')
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
@app.route('/java')
def java():
    return render_template('java.html')

@app.route('/todo')
def  todo():
   return render_template('todolist.html')

@app.route('/python')
def python():
    return render_template('python.html')

@app.route('/php')
def php():
    return render_template('php.html')
    
@app.route('/software')
def desk():
    items  = Database.find("blogs", {}).limit(2)
    todolist = Database.find("todo", {}).limit(2)
    
    if request.cookies.get('login_email') == "":
        flash("You  have logged out successfully")
        return  redirect(url_for('login_route'))
    return render_template('ecommerce.html' , items=items)
    
@app.route('/login')
def login_route():
        return render_template('login.html')


@app.route('/profile')
def profile():
    return redirect(url_for('index'))
    
@app.route('/author_profile')
def author_profile():
    return render_template('author_profile.html')

@app.route('/add_todo',  methods=['GET', 'POST'])
def addTodo():
    if request.method == 'POST':
        todoname = request.get_json()['todoName']
        
        description = request.get_json()['discription']
        login_cookies_email = request.cookies.get('login_email')
        photo = "photo.jpg"
        
        todo = Todo(todoname,photo, description,login_cookies_email)
        
        checkName  =  todo.checkName()
        checkDescription = todo.descriptionfun()
        data = todo.find_by_email(todo.todoname)
        
        print("this is Hangup")
       
        if checkName and  checkDescription == True:
            if data == False:
                todo.save_mongodb()
            else:
                return jsonify({"name":todoname, "discription":description})
        else:
            print("There is a problem")
        
    return   jsonify({"message":"please check the code"})
            
@app.route('/user_request',methods=['GET','POST'] )
def user_request():
    if  request.method  ==  'POST':
        print(request.get_json()['login_name'])
        login_cookie_email = request.cookies.get('login_email')
        
        #login user  details 
        login_name = request.get_json()['login_name']
        login_email = request.get_json()['login_email']
        login_id = request.get_json()['login_id']
        
        #post user details
        post_user = request.get_json()['post_name']
        post_email = request.get_json()['post_email']
        post_id  = request.get_json()['post_id']
        
        accept = request.get_json()['accept']
        count = request.get_json()['count']
        buttonstate = request.get_json()['button_state']
        
        
        coll  =  post_email
        
        if post_email != login_email and Request.get_by_title_request(post_email,  login_email) == False:
            Request.requests(login_name,  login_email, login_id,buttonstate,accept, count, coll,post_user)
            return jsonify({"login_name":login_name, "login_email":login_email,"login_id":login_id,"accept":accept, "count":count})
        else:
            print({"message":"the user tried to send request to it self.","post_email":post_email,"login_email":login_email
            })
            
    return   jsonify({"message":"please check the code"})
    
@app.route('/successful_reg')
def success_full_reg():
    if request.cookies.get('login_email') == "":
        flash("Thank you for  registering")
        return redirect(url_for('login_route'))
    return render_template('register.html')

@app.route('/register/page')
def register_route():
   regform = Form()
   return render_template('register.html', title='registration', regform=regform)

@app.route('/register')
def register():
   #regform = Form()
   return render_template('register.html', title='registration', regform="")

#url profile_picture
@app.route('/profile_picture_url')
def profile_piture_url():
    return render_template('uploadprofileImage.html')

#upload user profile picture 
@app.route('/picture', methods=['GET','POST'])
def profile_picture():
    if  request.method == 'POST':
        file = request.files['file']
        if file == '':
            print("No file  seleted file")
        if file.filename:
            
            email = request.cookies.get('login_email')
            filename = secure_filename(file.filename)
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            Users.save_image(email, filename)
            response = make_response(redirect(url_for('welcome', email=email)))
            response.set_cookie('login_email',request.cookies.get('login_email'))
            response.set_cookie('login_author', request.cookies.get('login_author'))
            response.set_cookie('login_id', request.cookies.get('login_id'))
            return response
        else:
            print("file type not allowed")
    
    return redirect(url_for('login_route'))
    
@app.route('/request')
def viewRequest():
    if request.cookies.get('login_email') is not None:
        if  request is not None:
            return  redirect(url_for('viewRequestHtml')) 
          
    return redirect(url_for('login_route'))
    
@app.route('/request_form')
def viewRequestHtml():
    if request.cookies.get('login_email') is not None:
        requests  = Database.find("requests"+request.cookies.get('login_email'), {})
        return render_template('viewRequest.html', requests=requests)
        
    return redirect(url_for('login_route'))
    
@app.route('/create_message')
def viewCreateMessage():
    if request.cookies.get('login_email') is not None:
        requests  = Database.find("requests"+request.cookies.get('login_email'), {})
        if request is not None:
            return  render_template('viewCreateMessage.html', requests=requests)
    return redirect(url_for('login_route'))
    
@app.route('/uploadVide')
def uploadVideo():
    if request.cookies.get('login_email') is not None:
        
        requests  = Database.find("requests"+request.cookies.get('login_email'), {})
        if  request is not None:
            return  render_template('uploadvideo.html', requests=requests)
    return redirect(url_for('login_route'))
    
@app.route('/friends')
def viewFriends():
    if request.cookies.get('login_email') is not None:
        friends  = Database.find("requests"+request.cookies.get('login_email'), {})
        if  request is not None:
            return  render_template('viewFriends.html', friends=friends)
    return redirect(url_for('login_route'))

@app.route('/message')
def viewMessage():
    if request.cookies.get('login_email') is not None:

        requests  = Database.find("messages"+request.cookies.get('login_email'), {})
        if  request is not None:
            return  render_template('ViewMessage.html', requests=requests)
    return redirect(url_for('login_route'))
    
@app.route('/register/process', methods=['GET', 'POST'])
def register_process():
    
   regform = Form(request.form)
 
   if request.method == 'POST':
       
       firstName=request.form['firstname'].lower()
       lastName =request.form['lastname'].lower()
       useremail=request.form['email'].lower()
       password =request.form['password'].lower()
       confirm_password  =request.form['confirm_password'].lower()
       birth    =request.form['birth'].lower()
       fileName =secure_filename(request.files['file'].filename.lower())

       
       
       size=128
       dig = md5(request.form['email'].lower().encode('utf-8')).hexdigest()
       image = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(dig, size)
       user_name = request.form['firstname'].lower()
       
       request.files['file'].save(os.path.join(os.getcwd() +'/static/uploads/reg', fileName))
       

       if  Users.get_by_email(request.form['email'].lower()) == False and password == confirm_password:
           registeremail  = Regmail(useremail)
           registeremail.send()
           Users.registration(firstName, lastName , useremail, password, fileName, image)
           
           return redirect(url_for('success_full_reg'))
       else:
           flash("The user name that you enter is forbiding please try again")
           return render_template('register.html', title='register', regform=regform)

   flash("there is a problem in the registration and   contact  the  adminstrator")
   return render_template('register.html', title='register', regform=regform)


@app.route('/changepass', methods=['GET' , 'POST'])
def changepass():
    session.pop('_flashes', None)
    if request.method == 'POST':
        if Users.get_by_email(request.form['email']) ==  True:
             if request.form['email'] != None:
                response = make_response(redirect(url_for('reqs', email=request.form['email'])))
                response.set_cookie('password_email', request.form['email'])
                return response
    else:    
        return render_template('login.html')
        
@app.route('/request/<string:email>')
def reqs(email):
    if Users.get_by_email(email) == True:
        return render_template('resetpass.html', email=email, confirmEmail='True')
    else:
        return  render_template('login.html')
        
@app.route('/confirm', methods=['GET', 'POST'])
def  passwordChanged():
    if request.method  == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        print({"firstpass":new_password, "secondpass":confirm_password})
        if  new_password  ==   confirm_password:
            print("They are equal")
            Users.resetPassword(request.cookies.get('password_email'), Users.passhashed(new_password))
            response = make_response(redirect(url_for('login_route')))
            response.set_cookie('password_email', "")
            return  response
    return  render_template('login.html')
         

@app.route('/', methods=['GET','POST'])
def login_process():
    #logform = LogForm()
    session.pop('_flashes', None)
    error = "There is a problem were you are not successfully logged in"
    if request.method == 'POST':
        try: 
                    email = request.form['email'].lower()
                    password = request.form['password'].lower()
                    
                    data =  Database.find_one(UserConstants.COLLECTION,{"email":email})
                    if Users.login_valid(request.form['email'],request.form['password']) != False  and utils.check_hash_password(password,data['password']) ==  True:
                        
                        session['login_email'] =  request.form['email']
                        session['login_password'] =  request.form['password']
                        
                
                        response = make_response(redirect(url_for('welcome')))
                        response.set_cookie('login_email', request.form['email'])
                        response.set_cookie('login_author', data['firstname'])
                        response.set_cookie('login_id', data['_id'])
                        return response
                        
                    else:
                        print("valid " + Users.login_valid(request.form['email'],request.form['password']))
                        print("password condition " + utils.check_hash_password(password,data['password']))
                        app.logger.warning('incorrect user name (%s)', request .form.get('name') )
                        flash("You are not a valiable  user")
                        render_template('login.html', title='login', logform=logform, error=error)
        except:
            print("An  exception  occured in login  process") 
                       
    flash('There is a problem were you are not successfully logged in')
    return render_template('login.html', title='login',error=error)
    

@app.route('/welcome')
def welcome():
   session.pop('_flashes', None)
   message = "You have  not logged in  please try  again"
   img = "image"

   if request.cookies.get('login_email') != "":
            #try:
                    check  = Database.find("blogs", {"email":request.cookies.get('login_email')})
                    userb  = Database.find("blogs", {"email":request.cookies.get('login_email')})
                    
                    date = datetime.datetime.utcnow()
                    item = Database.find_one(UserConstants.COLLECTION,{"email":request.cookies.get('login_email')})
                
                    uploads    = Database.find('myboo', {"useremail":request.cookies.get('login_email')})
                    com_text =   Database.find_one('profileImage', {"email":request.cookies.get('login_email')})
                    if com_text is not  None:
                        com_text = Users.text_avaliable(Database.find_one('profileImage', {"useremail":request.cookies.get('login_email')}))
                    elif com_text is None:
                        com_text =  "nothing here"
                        print(com_text)
                
                    
                    if  request.cookies.get('login_email') != "":
                    
                        #postobject = UserBlog(request.cookies.get('login_email'))
                        #blogs = postobject.blog_list()
                    
                     
                        #blogs      = Database.find("blogs", {"email":request.cookies.get('login_email')})
                        
                        pictures     =  Database.find('profileImage',{}).limit(4)
                        
                        saysomething = Database.find(request.cookies.get('login_email')+"saycomment", {'login_email':request.cookies.get('login_email')})
                        #youtube    = Database.find_one('user', {"email":request.cookies.get('login_email')})['youtube']
                        print(saysomething)
                        #no  need for a new collection
                        postsu     = Database.find(request.cookies.get('login_email')+"_"+"blog_posts", {})
                        comment_posts = Database.find("post_comments", {})
                        videos      = Database.find("videos",  {})
                        
                        
                        postUsers  = Database.find("blogs", {})
                        
                        length     = Database.find("requests"+request.cookies.get('login_email'), {})
                        
                        messageRe  = Database.find("requests"+request.cookies.get('login_email'), {})
                        requests   = Database.find("requests"+request.cookies.get('login_email'), {})
                        friends    = Database.find("requests"+request.cookies.get('login_email'), {})
                        requests = 0
                        #acccepted  = Database.find("requests"+request.cookies.get('login_email'), {}).count() - length
                        
                        #messages   = Database.find("requests"+request.cookies.get('login_email'),{}).count()
                        
                        userblog   = Database.find("blogs" ,{'email':item['email']})
                        email      = request.cookies.get('login_email') 
                        user       = Database.find_one('user', {"email":email})
                        
                        todolist = Database.find("todo", {}).limit(2)
                        
                        items = Database.find_one(UserConstants.COLLECTION,{"email":request.cookies.get('login_email')})
                        
                        img = File_system.image(request.cookies.get('login_email'))
                        flash('Login is a success' + " "+ 'welcome' + " "+ request.cookies.get('login_email'))
                        return render_template('index.html',videos=videos,comment_posts=comment_posts,pictures=pictures,requests=requests, messageRe=messageRe,friends=friends, email=request.cookies.get('login_email'),firstname=items['firstname'],_id=items['_id'],lastname = items['lastname'],date=date, login='true',image=items['image'], posts=postsu , userblog=userblog,user=user, Database=Database,  uploads=uploads, saysomething=saysomething)
                    else:
                        print("it doesnt work")
            #except:
               # print("An  exception  occured in the welcome")
            
   flash("There is a problem  login  you in")
   return redirect(url_for('login_route'))


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('out')))
    response.set_cookie('login_email', "",expires=0)
    response.set_cookie('login_author',"",expires=0)
    response.set_cookie('login_id', "",expires=0)
    return  response
 
 
@app.route('/outPage')
def  out():
    if request.cookies.get('login_email') is None:
        session.pop('_flashes', None)
        session.pop('login_email',None)
        response = make_response(redirect(url_for('desk')))
        response.set_cookie('login_email', "")
        response.set_cookie('login_author', "")
        response.set_cookie('login_id', "")
        return  response
    return redirect(url_for('welcome', email="none"))
    
if __name__== '__main__':
    host = os.getenv('IP','127.0.0.1')
    port = int(os.getenv('PORT',3000))
    app.secret_key = '\x0f\xf6\xc7\x11\x9c\xadC\xca\xf8$\xdeb\xde\x8bz \xbb\xcf\x9f\xbcC\xfd1.'
    app.run(host=host,port=port,debug=True)
