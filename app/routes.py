from app import app, db, mail
from flask import Flask, jsonify, flash, render_template, request, redirect, session, url_for
from app.models import User, Posts, Replies
from sqlalchemy import desc
from functools import wraps
from passlib.hash import sha256_crypt
from werkzeug.security import check_password_hash, generate_password_hash
import re
import secrets
import os
import random
from pathlib import Path
import calendar
from datetime import datetime, date
from flask_mail import Message
from sqlalchemy.exc import SQLAlchemyError


def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@login_required
@app.route("/posts", methods=["POST"])
def post():
    if "user" in session:
        post = request.form.get("post")
        rows = User.query.filter_by(username=session["user"]).first()

        user_id = rows.id
        posts = Posts.query.filter_by(user_id=user_id).all()
        if post != "":
            try:
                post = Posts(post, user_id)
                db.session.add(post)
                db.session.commit()

                return jsonify(success=1)

            except Exception as e:
                return jsonify(success=0, error_msg=e)
            return jsonify({'post': post, 'user_id': user_id})

        else:
            return jsonify({"message": "Post is empty!!"})
    else:
        return redirect(url_for("index"))


@login_required
@app.route("/like/<id>", methods=["POST"])
def like(id):

    if "user" in session:
        post = Posts.query.filter_by(id=id).first()
        post.likes += 1
        db.session.commit()
        return jsonify({'likes':post.likes})
    else:
        return redirect(url_for("index"))


def password_check(password):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    pattern = re.compile(reg)
    match = re.search(pattern, password)
    if match:
        return True
    return False


def date_convert(year, month, day):
    try:
        dob = date(int(year), int(month), int(day))
        return dob
    except:
        return flash("Date couldn't convert!")


def user_exist(user, email):
    user_db = User.query.filter_by(email=email).first_or_404()
    if user == user_db.email:
        flash("User already exist!! Login or reset password by clicking forget password!!")
        return True
    else:
        return False


def save_photo(photo):
    photo_f = secrets.token_hex(8)
    _, ext = os.path.splitext(photo.filename)
    print(ext)
    photoname = photo_f + ext
    photo_path = os.path.join(os.getcwd(), 'app\static\images', photoname)
    photo.save(photo_path)
    return photoname


@login_required
@app.route("/delete-comment/<id>", methods=["POST"])
def delete_comment(id):
    if "user" in session:

        comment_to_delete = Replies.query.get_or_404(id)
        user = User.query.filter_by(username=session["user"]).first()
        post_id = comment_to_delete.post_id
        post = Posts.query.get_or_404(post_id)
        if comment_to_delete.user_id == user.id:
            try:

                post.comments -= 1
                db.session.delete(comment_to_delete)
                db.session.commit()

                return jsonify(success=1)
            except:
                return jsonify(success=0)
        else:
            return jsonify({'error': "can't delete other comment!!"})
    else:
        return redirect(url_for("index"))


@login_required
@app.route("/delete/<id>", methods=["get", "POST"])
def delete_post(id):
    if "user" in session:
        if request.method == "POST":
            post_to_delete = Posts.query.get_or_404(id)
            comment_to_delete = Replies.query.filter(
                Replies.post_id == post_to_delete.id).all()
            if post_to_delete.user.username == session["user"]:
                try:
                    for comment in comment_to_delete:
                        db.session.delete(comment)
                    db.session.delete(post_to_delete)
                    db.session.commit()
                    return jsonify(success=1)

                except:
                    return jsonify(success=0)
    else:

        return redirect(url_for('index'))


@login_required
@app.route("/update_post/<id>", methods=["GET", "POST"])
def update_post(id):
    post_to_update = Posts.query.get_or_404(id)
    post = request.form.get("post")
    try:
        post_to_update.post = post
        db.session.commit()

        if request.endpoint == "user":
            return redirect(url_for('user_index'))
        else:
            return redirect(url_for('user_home', username=session["user"]))
    except:
        flash("There is problems on updating post!")
        if request.endpoint == "user":
            return redirect(url_for('user_index'))
        else:
            return redirect(url_for('user_home', username=session["user"]))


@login_required
@app.route("/update", methods=["GET", "POST"])
def update():
    user = session["user"]
    if request.method == "GET":
        if user:
            months = list(calendar.month_name[1:])
            year_date = datetime.now()
            year_now = year_date.year
            user_data = User.query.filter_by(username=session["user"]).first()
            checked = user_data.gender
            return render_template("users/update.html", checked=checked, user=user, user_data=user_data, months=months, year_now=year_now)
        else:
            return redirect(url_for("index"))
    else:
        name = request.form.get("name")
        day = request.form.get("day")
        month = request.form.get("month")
        year = request.form.get("year")
        dob = date_convert(year, month, day)
        gender = request.form.get("gender")
        user_photo = request.files["profile_photo"]

        user_data = User.query.filter_by(username=session["user"]).first()
        if user_photo:
            profile_photo = save_photo(user_photo)
            user_data.user_profile = profile_photo
        user_data.name = name
        user_data.dob = dob
        user_data.gender = gender
        db.session.commit()

        if request.endpoint == "user":
            return redirect(url_for('user_index'))
        else:
            return redirect(url_for('user_home', username=session["user"]))


@login_required
@app.route("/reply/<id>", methods=["POST"])
def reply(id):
    if "user" in session:
        rply_text = request.form.get("reply")
        rows = User.query.filter_by(username=session["user"]).first()
        user_id = rows.id
        post_id = id
        reply_insert = Replies(rply_text, user_id, post_id)
        try:
            db.session.add(reply_insert)
            post = Posts.query.filter_by(id=id).first()
            post.comments += 1
            db.session.commit()
            return jsonify(success=1)
        except:
            return jsonify(success=0)
        return jsonify({"user_id": user_id, "post_id": post_id})
    else:
        return redirect(url_for('index'))


@login_required
@app.route("/search", methods=["POST", "GET"])
def search():
    
    if "user" in session:
        search_user = request.form.get("search")
        results = db.session.query(User).filter(
            User.name.like('%{}%'.format(search_user))).all()
        user = session["user"]
        user_id = User.query.filter_by(username=user).first()
        
        # jrows = jsonify(rows)
        user_s_id = user_id.id
        
        return render_template("users/search.html",results=results,search_user=search_user, user=user,  user_s_id=user_s_id)
    else:
        flash("login required")
        return redirect("/")
    return render_template("users/search.html", user=user)
    


@app.route('/login', endpoint='login', methods=["POST"])
def login():
    session.clear()

    if not None:
        email = request.form.get("email_login")
        password = request.form.get("password")
        rows = User.query.filter_by(email=email).first()
        if rows != None:
            if email == rows.email and check_password_hash(rows.password, password):

                rows.acitve = 1
                db.session.commit()

                session['user'] = rows.username
                return redirect(url_for('user_home', username=session["user"]))
            else:
                flash("email or password not matched")
                return redirect("/")
        else:
            flash(f"You don't have account, please create new account {email}")
            return redirect("/")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        months = list(calendar.month_name[1:])
        year_date = datetime.now()
        year_now = year_date.year
        ctrpath = os.path.join(os.getcwd(), "app\static\css\countries.txt")

        list_of_country = open(ctrpath)

        return render_template("index.html", months=months, year_now=year_now, countries=list_of_country)
    else:

        if request.endpoint != 'login':
            username = request.form.get("username")
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            cpassword = request.form.get("cpassword")
            day = request.form.get("day")
            month = request.form.get("month")
            year = request.form.get("year")
            dob = date_convert(year, month, day)
            gender = request.form.get("gender")
            nationality = request.form.get("nationality")
            match = password_check(password)
            if match:
                if password == cpassword:
                    password = generate_password_hash(password)
                    user = User(username, name, email, password,
                                dob, nationality, gender)
                    try:
                        db.session.add(user)
                        db.session.commit()

                    except SQLAlchemyError as e:
                        flash("Couldn't register the account, check required field ")
                        db.session.rollback()
                        return redirect(request.url)

                    else:
                        flash("User Successfully Added")
                        session['user'] = username
                        return redirect(url_for('user_home', username=session["user"]))
                else:
                    flash("Password didn't match")
                    return redirect("/")
            else:
                flash("Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character")
                return redirect("/")


@app.route("/reset-password", methods=["POST", "GET"])
def reset():
    if request.method == "GET":
        return render_template("users/resetpass.html")
    else:
        if request.endpoint != 'login':
            email = request.form.get("email_request")
            user = User.query.filter_by(email=email).first_or_404()
            if user:
                def get_random_string(length=24, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
                    return ''.join(random.choice(allowed_chars) for i in range(length))
                hashcode = get_random_string()
                user.hashCode = hashcode
                db.session.commit()

                msg = Message("Password Reset Request",
                              sender="noreply@demo.com", recipients=[user.email])
                msg.body = "Hello,\nWe've received a request to reset your password. If you want to reset your password, click the link below and enter your new password\n http://localhost:5000/reset-password/" + user.hashCode
                mail.send(msg)
                print(msg)
                flash("Message has been sent to email")
                return redirect("/")

            else:
                flash("email not found")
                return redirect("/")


@app.route("/reset-password/<string:hashCode>", methods=["GET", "POST"])
def hashcode(hashCode):
    hash_check = User.query.filter_by(hashCode=hashCode).first()
    hashed = hash_check.hashCode
    if hash_check:
        if request.method == 'POST' and request.endpoint != "login":
            password = request.form['password']
            cpassword = request.form['cpassword']

            print(password)
            if password == cpassword:
                check = password_check(password)
                if check:
                    hash_check.password = generate_password_hash(password)
                    hash_check.hashCode = None
                    db.session.commit()

                    flash("Successfully changed your password!")
                    return redirect(url_for('user_home', username=session["user"]))
                else:
                    print("into")
                    flash(
                        "Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character")
                    return redirect(request.referrer)
            else:
                flash("password didn't match!")
                return redirect(request.url)
        else:

            return render_template("users/passresetform.html", hashed=hashed)


@login_required
@app.route("/user", methods=["POST", "GET"])
def user_index():
    if "user" in session:
        if request.method == "GET":
            user = session["user"]
            rows = User.query.filter_by(username=user).first()
            users = User.query.all()
            date = rows.created_at
            date_created = rows.created_at.strftime("%Y-%m-%d")
            status = rows.acitve
            if status == True:
                status = "Online"
            else:
                status = "Offline"

            user_id = rows.id
            posts = Posts.query.order_by(desc(Posts.posted_on)).all()
            image_file = url_for(
                'static', filename="images/" + rows.user_profile)
            replies_all = Replies.query.all()
            return render_template("users/homepage.html", user_id=user_id, users=users, user=user, rows=rows, status=status, posts=posts, replies_all=replies_all, image_file=image_file)
    else:
        return redirect(url_for("index"))


@login_required
@app.route("/user/<username>", methods=["POST", "GET"])
def user_home(username):
    if "user" in session:
        user = session["user"]
        rows = User.query.filter_by(username=username).first()
        date = rows.created_at
        date_created = rows.created_at.strftime("%Y-%m-%d")
        status = rows.acitve

        if status == True:
            status = "Online"
        else:
            status = "Offline"

        user_id = rows.id
        posts = Posts.query.order_by(desc(Posts.posted_on)).all()
        post = Replies.query.order_by(desc(Replies.replied_on)).first()
        image_file = url_for('static', filename="images/" + rows.user_profile)
        replies_all = Replies.query.all()
        users = User.query.all()
        rows = User.query.filter_by(username=username).first()
        if session["user"] == rows.username:
            rows.acitve = 1
        db.session.commit()

        return render_template("users/user_home.html", username=username, users=users, user=user, rows=rows, status=status, posts=posts, replies_all=replies_all, image_file=image_file)
    else:
        flash("Login Required")
        return redirect("/")


@app.route("/logout")
def logout():
    if "user" in session:
        rows = User.query.filter_by(username=session['user']).first()
        rows.acitve = 0
        db.session.commit()

    session.clear()
    flash("Logged out successfully!")
    return redirect("/")


@app.errorhandler(404)
def not_found(e):
    if 'user' in session:
        return render_template("users/404.html")
    else:
        return redirect(url_for('index'))


@app.before_request
def clear_trailing():
    rp = request.path
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1])


@app.errorhandler(405)
def not_found(e):
    if 'user' in session:
        return render_template("users/405.html")
    else:
        return redirect(url_for('index'))


if __name__ == "__main__":

    app.run()
