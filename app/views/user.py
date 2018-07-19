# -*- coding: utf-8 -*-
import bcrypt
import json
import re
from csv import writer
from datetime import datetime
from flask import Blueprint
from flask import flash, redirect, render_template, request, url_for, abort, \
    session
from flask_babel import _
from flask_login import current_user, login_user, logout_user, login_required
from io import StringIO

from app import db, login_manager, get_locale
from app.decorators import require_role, response_headers
from app.exceptions.base import ResourceNotFoundException, \
    AuthorizationException, ValidationException
from app.forms import init_form
from app.forms.user import (EditUserForm, EditUserInfoForm, SignUpForm,
                            SignInForm, ResetPasswordForm, RequestPassword,
                            ChangePasswordForm)
from app.models.activity import Activity
from app.models.custom_form import CustomFormResult, CustomForm
from app.models.education import Education
from app.models.user import User
from app.roles import Roles
from app.service import password_reset_service, user_service, \
    role_service, mail_service, file_service
from app.utils import copernica
from app.utils.google import HttpError
from app.utils.user import UserAPI

blueprint = Blueprint('user', __name__)


@login_manager.user_loader
def load_user(user_id):
    # The hook used by the login manager to get the user from the database by
    # user ID.
    return user_service.get_user_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(
        url_for("user.sign_in",
                next=url_for("oauth.authorize", **request.args)))


def view_single(user_id):
    """
    View user for admins and edit for admins and users.

    User is passed based on routes below.
    """
    user = user_service.get_user_by_id(user_id)
    user.avatar = UserAPI.avatar(user)
    user.groups = UserAPI.get_groups_for_user_id(user)

    user.groups_amount = len(user.groups)

    if "gravatar" in user.avatar:
        user.avatar = user.avatar + "&s=341"

    # Get all activity entrees from these forms, order by start_time of
    # activity.
    activities = Activity.query.join(CustomForm).join(CustomFormResult). \
        filter(CustomFormResult.owner_id == user_id and
               CustomForm.id == CustomFormResult.form_id and
               Activity.form_id == CustomForm.id)

    user.activities_amount = activities.count()

    new_activities = activities \
        .filter(Activity.end_time > datetime.today()).distinct() \
        .order_by(Activity.start_time)
    old_activities = activities \
        .filter(Activity.end_time < datetime.today()).distinct() \
        .order_by(Activity.start_time.desc())

    can_write = role_service.user_has_role(current_user, Roles.USER_WRITE)

    return render_template('user/view_single.htm', user=user,
                           new_activities=new_activities,
                           old_activities=old_activities,
                           can_write=can_write)


@blueprint.route('/users/view/self/', methods=['GET'])
@login_required
def view_single_self():
    return view_single(current_user.id)


@blueprint.route('/users/view/<int:user_id>/', methods=['GET'])
@require_role(Roles.USER_READ)
@login_required
def view_single_user(user_id):
    return view_single(user_id=user_id)


@blueprint.route('/users/remove_avatar/<int:user_id>/', methods=['DELETE'])
@login_required
@require_role(Roles.USER_WRITE)
def remove_avatar(user_id=None):
    user = user_service.get_user_by_id(user_id)
    if current_user.is_anonymous or current_user.id != user_id:
        return "", 403

    user_service.remove_avatar(user.id)
    return "", 200


def edit(user_id, form_cls):
    """
    Create user for admins and edit for admins and users.

    User and form type are passed based on routes below.
    """
    if user_id:
        user = user_service.get_user_by_id(user_id)
        user.avatar = user_service.user_has_avatar(user_id)
    else:
        user = User()

    form = init_form(form_cls, obj=user)
    form.new_user = user.id == 0

    # Add education.
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    def edit_page():
        is_admin = role_service.user_has_role(current_user, Roles.USER_WRITE)
        return render_template('user/edit.htm', form=form, user=user,
                               is_admin=is_admin)

    if form.validate_on_submit():

        # Only new users need a unique email.
        query = User.query.filter(User.email == form.email.data)
        if user_id:
            query = query.filter(User.id != user_id)

        if query.count() > 0:
            flash(_('A user with this e-mail address already exist.'),
                  'danger')
            return edit_page()

        # Because the user model is constructed to have an ID of 0 when it is
        # initialized without an email adress provided, reinitialize the user
        # with a default string for email adress, so that it will get a unique
        # ID when committed to the database.
        if not user_id:
            user = User('_')

        try:
            user.update_email(form.email.data.strip())
        except HttpError as e:
            if e.resp.status == 404:
                flash(_('According to Google this email does not exist. '
                        'Please use an email that does.'), 'danger')
                return edit_page()
            raise e

        user.first_name = form.first_name.data.strip()
        user.last_name = form.last_name.data.strip()
        user.locale = form.locale.data
        if role_service.user_has_role(current_user, Roles.USER_WRITE):
            user.has_paid = form.has_paid.data
            user.honorary_member = form.honorary_member.data
            user.favourer = form.favourer.data
            user.disabled = form.disabled.data
            user.alumnus = form.alumnus.data
        user.student_id = form.student_id.data.strip()
        user.education_id = form.education_id.data
        user.birth_date = form.birth_date.data
        user.study_start = form.study_start.data
        user.receive_information = form.receive_information.data

        user.phone_nr = form.phone_nr.data.strip()
        user.address = form.address.data.strip()
        user.zip = form.zip.data.strip()
        user.city = form.city.data.strip()
        user.country = form.country.data.strip()

        db.session.add(user)
        db.session.commit()

        avatar = request.files.get('avatar')
        if avatar:
            user_service.set_avatar(user.id, avatar)

        if user_id:
            copernica.update_user(user)
            flash(_('Profile succesfully updated'))
        else:
            copernica.update_user(user, subscribe=True)
            flash(_('Profile succesfully created'))

        if current_user.id == user_id:
            return redirect(url_for('user.view_single_self'))
        else:
            return redirect(url_for('user.view_single_user', user_id=user.id))

    return edit_page()


@blueprint.route('/users/edit/self/', methods=['GET', 'POST'])
@login_required
def edit_self():
    return edit(current_user.id, EditUserInfoForm)


@blueprint.route('/users/create/', methods=['GET', 'POST'])
@blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@require_role(Roles.USER_WRITE)
def edit_user(user_id=None):
    return edit(user_id, EditUserForm)


@blueprint.route('/sign-up/', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def sign_up():
    # Redirect the user to the index page if he or she has been authenticated
    # already.
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    form = SignUpForm(request.form)

    # Add education.
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    if form.validate_on_submit():
        query = User.query.filter(User.email == form.email.data)

        if query.count() > 0:
            flash(_('A user with this e-mail address already exists'),
                  'danger')
            return render_template('user/sign_up.htm', form=form)

        user = User(form.email.data,
                    bcrypt.hashpw(form.password.data.encode('utf-8'),
                                  bcrypt.gensalt()),
                    form.first_name.data,
                    form.last_name.data, form.student_id.data,
                    form.education_id.data, form.birth_date.data,
                    form.study_start.data, form.receive_information.data)
        user.phone_nr = form.phone_nr.data
        user.address = form.address.data
        user.zip = form.zip.data
        user.city = form.city.data
        user.country = form.country.data

        db.session.add(user)
        db.session.commit()

        db.session.commit()

        copernica.update_user(user, subscribe=True)

        if get_locale() == 'nl':
            mail_template = 'email/sign_up_nl.html'
        else:
            mail_template = 'email/sign_up_en.html'

        mail_service.send_mail(
            user.email, _('Welcome to via, %(name)s', name=user.first_name),
            mail_template, user=user)

        login_user(user)

        flash(_('Welcome %(name)s! Your profile has been succesfully '
                'created and you have been logged in!',
                name=current_user.first_name), 'success')

        return redirect(url_for('home.home'))

    return render_template('user/sign_up.htm', form=form)


@blueprint.route('/sign-in/', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def sign_in():
    # Redirect the user to the index page if he or she has been authenticated
    # already.

    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    form = SignInForm(request.form)

    if form.validate_on_submit():

        try:
            user = user_service.get_user_by_login(form.email.data,
                                                  form.password.data)

            # Notify the login manager that the user has been signed in.
            login_user(user)

            next_ = request.args.get("next", '')
            if next_ and next_.startswith("/"):
                return redirect(next_)

            # If referer is empty for some reason (browser policy, user entered
            # address in address bar, etc.), use empty string
            referer = request.headers.get('Referer', '')

            denied = (
                re.match(r'(?:https?://[^/]+)%s$' % (url_for('user.sign_in')),
                         referer) is not None)
            denied_from = session.get('denied_from')

            if not denied:
                if referer:
                    return redirect(referer)
            elif denied_from:
                return redirect(denied_from)

            return redirect(url_for('home.home'))

        except ResourceNotFoundException:
            flash(_(
                'It appears that account does not exist. Try again, or contact'
                ' the website administration at ict (at) svia (dot) nl.'))
        except AuthorizationException:
            flash(_('Your account has been disabled, you are not allowed '
                    'to log in'), 'danger')
        except ValidationException:
            flash(_('The password you entered appears to be incorrect.'))

    return render_template('user/sign_in.htm', form=form)


@blueprint.route('/sign-out/')
def sign_out():
    # Notify the login manager that the user has been signed out.
    logout_user()

    flash(_('Captain\'s log succesfully ended.'), 'success')

    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)

    return redirect(url_for('home.home'))


@blueprint.route('/request_password/', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def request_password():
    """Create a ticket and send a email with link to reset_password page."""
    if current_user.is_authenticated:
        return redirect(url_for('user.view_single_self'))

    form = RequestPassword(request.form)

    if form.validate_on_submit():
        try:
            password_reset_service.create_password_ticket(form.email.data)
            flash(_('An email has been sent to %(email)s with further '
                    'instructions.', email=form.email.data), 'success')
            return redirect(url_for('home.home'))

        except ResourceNotFoundException:
            flash(_('%(email)s is unknown to our system.',
                    email=form.email.data), 'danger')

    return render_template('user/request_password.htm', form=form)


@blueprint.route('/reset_password/<string:hash_>', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def reset_password(hash_):
    """
    Reset form existing of two fields, password and password_repeat.

    Checks if the hash in the url is found in the database and timestamp
    has not expired.
    """
    try:
        ticket = password_reset_service.get_valid_ticket(hash_)
    except ResourceNotFoundException:
        flash(_('No valid ticket found'), 'danger')
        return redirect(url_for('user.request_password'))

    form = ResetPasswordForm(request.form)

    if form.validate_on_submit():
        password_reset_service.reset_password(ticket, form.password.data)
        flash(_('Your password has been updated.'), 'success')
        return redirect(url_for('user.sign_in'))

    return render_template('user/reset_password.htm', form=form)


@blueprint.route("/users/<int:user_id>/password/", methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def change_password(user_id):
    if (user_id is not None and current_user.id != user_id and
            not role_service.user_has_role(current_user, Roles.USER_WRITE)):
        abort(403)

    form = ChangePasswordForm()

    if form.validate_on_submit():
        if user_service.validate_password(current_user,
                                          form.current_password.data):
            user_service.set_password(current_user.id,
                                      form.password.data)
            flash(_("Your password has successfully been changed."))
            return redirect(url_for("home.home"))
        else:
            form.current_password.errors.append(
                _("Your current password does not match."))
    return render_template("user/change_password.htm", form=form)


@blueprint.route('/users/', methods=['GET', 'POST'])
@require_role(Roles.USER_READ)
def view():
    return render_template('user/view.htm')


@blueprint.route('/users/export', methods=['GET'])
@require_role(Roles.USER_READ)
def user_export():
    users = User.query.all()
    si = StringIO()
    cw = writer(si)
    cw.writerow([c.name for c in User.__mapper__.columns])
    for user in users:
        cw.writerow([getattr(user, c.name) for c in User.__mapper__.columns])
    return si.getvalue().strip('\r\n')


@blueprint.route('/users/avatar/<int:user_id>/', methods=['GET'])
@login_required
def view_avatar(user_id=None):
    can_read = False

    # Unpaid members cannot view other avatars
    if current_user.id != user_id and not current_user.has_paid:
        return abort(403)

    # A user can always view his own avatar
    if current_user.id == user_id:
        can_read = True

    # group rights
    if role_service.user_has_role(current_user, Roles.USER_READ) \
            or role_service.user_has_role(current_user, Roles.USER_WRITE) \
            or role_service.user_has_role(current_user, Roles.ACTIVITY_WRITE):
        can_read = True

    if not can_read:
        return abort(403)

    if not user_service.user_has_avatar(user_id):
        return abort(404)

    user = user_service.get_user_by_id(user_id)

    avatar_file = file_service.get_file_by_id(user.avatar_file_id)

    fn = 'user_avatar_' + str(user.id)

    content = file_service.get_file_content(avatar_file)
    headers = file_service.get_file_content_headers(
        avatar_file, display_name=fn)

    return content, headers


###
# Here starts the public api for users
###
@blueprint.route('/users/get_users/', methods=['GET'])
@require_role(Roles.USER_READ)
def get_users():
    users = User.query.all()
    user_list = []

    for user in users:
        user_list.append(
            [user.id,
             user.email,
             user.first_name,
             user.last_name,
             user.student_id,
             user.education.name
             if user.education else "",
             "<i class='glyphicon glyphicon-ok'></i>"
             if user.has_paid else "",
             "<i class='glyphicon glyphicon-ok'></i>"
             if user.honorary_member else "",
             "<i class='glyphicon glyphicon-ok'></i>"
             if user.favourer else "",
             "<i class='glyphicon glyphicon-ok'></i>"
             if user.alumnus else ""
             ])
    return json.dumps({"data": user_list})
