from flask import render_template, flash, redirect,  url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, AccountSettingsForm, UploadPlan, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, ImageUpload
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email

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


@app.route('/account/<email>')
@login_required
def account(email):
    user = User.query.filter_by(email=email).first_or_404()
    return render_template('account.html', user=user)


@app.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    form = AccountSettingsForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('account_settings'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('account_settings.html', title='Account Settings', form=form)


@app.route('/doc_checker', methods=['GET', 'POST'])
@login_required
def doc_checker():
    form = UploadPlan()
    if form.validate_on_submit():
        plan = ImageUpload(image=form.plan.data, uploader_id=current_user)
        db.session.add(plan)
        db.session.commit()
        flash('your plan is uploaded')
        return redirect(url_for('doc_checker'))
    return render_template('doc_checker.html', title='Document Checker', form=form)


@app.route('/processed_image_review', methods=['GET', 'POST'])
@login_required
def processed_image_review():
    page = request.args.get('page', 1, type=int)
    images = current_user.image_uploads.order_by(ImageUpload.timestamp.desc()).paginate(page, app.config['IMAGES_PER_PAGE'], False)
    next_url = url_for('processed_image_review', email=current_user.email, page=images.next_num) \
        if images.has_next else None
    prev_url = url_for('processed_image_review', email=current_user.email, page=images.prev_num) \
        if images.has_prev else None
    return render_template('processed_image_review.html', images=images.items, next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


from app.forms import ResetPasswordForm

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
# def create_tables():
#     db.create_all()
