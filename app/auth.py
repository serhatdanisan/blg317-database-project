from flask import request, render_template, Blueprint, redirect, url_for, session, flash
from authHelper import getUser, registerUser, deleteUser
from werkzeug.security import generate_password_hash, check_password_hash
import functools

def isAdmin(view):
    @functools.wraps(view)
    def wrappedView(**kwargs):
        if session.get('role') is not None:
            if session['role']==1:
                pass
            else:
                return 'You are not authorized for admin role!'
        else:
            return 'You are not logged in!'
        return view(**kwargs)

    return wrappedView

def loginRequired(view):
    @functools.wraps(view)
    def wrappedView(**kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrappedView

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') # do not change!!
        user = getUser(username)
        if user is None:
            error = 'Incorrect username.'

        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'
        else:
            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[3]
            session['role'] = user[4]
            return redirect(url_for('home'))
            
    return render_template('account/login.html', error=error)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') # do not change!
        email = request.form.get('email')
        pswHash = generate_password_hash(password)
        error = registerUser(username, pswHash, email, role=0) 
        if error is None:
            return redirect(url_for('auth.login'))
    
    return render_template('account/register.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@auth_bp.route('/user', methods=['GET', 'POST'])
@loginRequired
def user():
    error = None
    if request.method == 'POST':
        # Delete user
        if request.form.get('username') is None:
            error = deleteUser(session['user_id'])
            if error is None:
                session.clear()
                return render_template('base.html')
        # Update
        else:
            error = updateUser({
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'user_id': session['user_id']
                })
            
            if error is None:
                user = getUser(request.form.get('username'))
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[4] # True is for admin False is for user

        
    return render_template('account/user.html', error=error)