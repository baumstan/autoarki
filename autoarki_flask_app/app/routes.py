from flask import render_template, flash, redirect,  url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm,EditAccountForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')


@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/doc_checker')
@login_required
def doc_checker():
    return render_template('doc_checker.html', title='Document Checker')


@app.route('/dock_checker/processed_image_review')
@login_required
def processed_image_review():
    images = [
        {
            'title': 'test_title',
            'page_num': '1',
            'output': 'test_output1'
        },
        {
            'title': 'test_title',
            'page_num': '2',
            'output': 'test_output2'
        }
    ]
    return render_template('processed_image_review.html', title='Processed Image', images=images)


@app.route('/account/<email>')
@login_required
def account(email):
    user = User.query.filter_by(email=email).first_or_404()
    images = [
        {
            'title': 'test_title',
            'page_num': '1',
            'output': 'test_output1',
            'timestamp': 'sometime'
        },
        {
            'title': 'test_title',
            'page_num': '2',
            'output': 'test_output2',
            'timestamp': 'sometime'
        }
    ]
    return render_template('account.html', user=user, images=images)


@app.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    form = EditAccountForm(current_user.email)
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('account_settings'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('account_settings.html', title='Account Settings',
                           form=form)
