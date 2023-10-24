from flask import Blueprint, request, render_template, redirect, Response, g, url_for
from memeapp.utils import cryptoutils
from memeapp.utils.dbutils import db_query, db_execute
from memeapp.utils.authutils import set_session_token, login_required, clear_session_token

bp = Blueprint("users", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect("/")
    username = request.form.get("username", None)
    password = request.form.get("password", None)
    user = db_query(f"SELECT rowid, password_hash FROM users WHERE username='{username}'", one=True)
    if user:
        user_id = user[0]
        password_hash = user[1]
        if cryptoutils.check_password(password, password_hash):
            response = redirect("/")
            set_session_token(user_id, response)
            return response
        else:
            return redirect("/login?error=Invalid+login")
    else:
        return redirect("/login?error=Invalid+login")


@bp.route("/logout", methods=["GET"])
def logout():
    response = redirect("/") #TODO: target the sign in form rather than the sign up form
    clear_session_token(response)
    g.user = None
    return response

@bp.route("/users", methods=["GET", "POST"])
def create_edit_user():
    errors = []
    warnings = []
    infos = []
    successes = []

    username = request.form.get("username", None) #used for create, but not edit
    name = request.form.get("name", None)
    password = request.form.get("password", None)
    passwordConfirm = request.form.get("passwordConfirm", None)
    currentPassword = request.form.get("currentPassword", None) #used for create, but not edit

    is_admin = int(request.form.get("a", 0))
    if is_admin > 0:
        if not g.user or not g.user.is_admin:
            is_admin = 0

    # If there is no current user we assume that they are registering a new user vs editing an old one
    editing = not not g.user

    if not name:
        errors.append("Name is required")

    if editing:
        #Current password is required in order to change any information
        if currentPassword == None or currentPassword == "":
            errors.append("Please enter your current password")
        else:
            #TODO: this is a copy and paste of the login related code with minor differences (no user_id here).  we should look for a way to unify them
            user = db_query(f"SELECT password_hash FROM users WHERE username=?", (g.user.username,), one=True)
            if user:
                password_hash = user[0]
                if not cryptoutils.check_password(currentPassword, password_hash):
                    errors.append("Current password does not match what is on file.")

        # An empty "new" password is ok when editing.  
        # They do not need to change their password when they change their display name.  
        # If they do change their password they need to match
        emptyPassword = not password
        emptyConfirmPassword = not passwordConfirm or passwordConfirm == ''
        updatedPasswordsMatch = (password == passwordConfirm) or (emptyPassword and emptyConfirmPassword)
        if not updatedPasswordsMatch:
            errors.append("Passwords do not match")
    else:
        if username == None or username == "":
            errors.append("No username provided")
        if password == None or password == "":
            errors.append("Please choose a password")
        if password != passwordConfirm:
            errors.append("Passwords do not match")

    if len(errors) == 0:
        if editing:
            if password:
                pw_hash = cryptoutils.hash_password(password).decode("utf-8")
            else:
                pw_hash = None #Don't reset the password, let the COALESCE keep the password the same when they have only changes non-password related fields
            print("Attempting to update the user", name, pw_hash, g.user.id)
            db_execute("UPDATE users SET name = COALESCE(?, name), password_hash = COALESCE(?, password_hash) WHERE rowid=?",
                                p=(name, pw_hash, g.user.id))
            successes.append("User updated")
            #update the user visible fields
            g.user.name = name 
        else:  #Create the user
            print("Attempting to create the user")
            if isExistingUser(username):
                errors.append(f"Username '{username}' is not available")
            else:
                pw_hash = cryptoutils.hash_password(password)
                user_id = db_execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                                     p=(username, name, pw_hash.decode("utf-8"), is_admin))
                response = redirect("/home")
                set_session_token(user_id, response)

                return response
    if g.user:
        # TODO: return in a way that keeps form fields populated, rather than resets them
        return render_template("profile/editProfile.html", user=g.user, errors=errors, warnings=warnings, infos=infos, successes=successes)
    else:
        return render_template("authenticate.html", errors=errors, warnings=warnings, infos=infos, successes=successes)

def isExistingUser(userName):
    existing_user = db_query("SELECT username FROM users WHERE username=?", p=(userName,), one=True)
    return not not existing_user

@bp.route("/users/<user_id>", methods=['GET'])
@login_required
def get_user(user_id=0):
    result = db_query("SELECT rowid, username, name FROM users WHERE rowid=?", (user_id,), True)
    if result and len(result) == 3:
        record_id, username, name = result
        user_record = {'id': record_id, 'username': username, 'name': name}

        memeCount = db_query("SELECT count(*) AS c FROM memes WHERE owner=?", (user_id,), True)
        commentCount = db_query("SELECT count(*) AS c FROM comments WHERE author=?", (user_id,), True)

        return render_template("profile/viewProfile.html", user=user_record, memeCount=memeCount[0], commentCount=commentCount[0])
    return Response("Not found", 404)
