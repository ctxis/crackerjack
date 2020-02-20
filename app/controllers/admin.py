from flask import Blueprint, current_app
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
import os
from app.lib.base.provider import Provider
from app.lib.models.user import UserModel


bp = Blueprint('admin', __name__)


@bp.route('/settings/hashcat', methods=['GET'])
@login_required
def settings_hashcat():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()

    return render_template(
        'admin/settings/hashcat.html'
    )


@bp.route('/settings/hashcat/save', methods=['POST'])
@login_required
def settings_hashcat_save():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    settings = provider.settings()

    hashcat_binary = request.form['hashcat_binary'].strip()
    hashcat_rules_path = request.form['hashcat_rules_path'].strip()
    hashcat_status_interval = request.form['hashcat_status_interval'].strip()
    hashcat_force = int(request.form.get('hashcat_force', 0))

    has_errors = False
    if len(hashcat_binary) == 0 or not os.path.isfile(hashcat_binary):
        has_errors = True
        flash('Hashcat executable does not exist', 'error')
    elif not os.access(hashcat_binary, os.X_OK):
        has_errors = True
        flash('Hashcat file is not executable', 'error')

    if len(hashcat_rules_path) == 0 or not os.path.isdir(hashcat_rules_path):
        has_errors = True
        flash('Hashcat rules directory does not exist', 'error')
    elif not os.access(hashcat_rules_path, os.R_OK):
        has_errors = True
        flash('Hashcat rules directory is not readable', 'error')

    if len(hashcat_status_interval) == 0:
        has_errors = True
        flash('Hashcat Status Interval must be set', 'error')

    hashcat_status_interval = int(hashcat_status_interval)
    if hashcat_status_interval <= 0:
        hashcat_status_interval = 10

    if has_errors:
        return redirect(url_for('admin.settings_hashcat'))

    settings.save('hashcat_binary', hashcat_binary)
    settings.save('hashcat_rules_path', hashcat_rules_path)
    settings.save('hashcat_status_interval', hashcat_status_interval)
    settings.save('hashcat_force', hashcat_force)

    # When settings are saved, run system updates.
    system = provider.system()
    system.run_updates()

    flash('Settings saved', 'success')
    return redirect(url_for('admin.settings_hashcat'))


@bp.route('/settings/auth', methods=['GET'])
@login_required
def settings_auth():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()

    return render_template(
        'admin/settings/auth.html'
    )


@bp.route('/settings/auth/save', methods=['POST'])
@login_required
def settings_auth_save():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    settings = provider.settings()

    allow_logins = request.form.get('allow_logins', 0)

    ldap_enabled = int(request.form.get('ldap_enabled', 0))
    ldap_ssl = int(request.form.get('ldap_ssl', 0))
    ldap_bind_pass = request.form['ldap_bind_pass'].strip()

    # Put the rest of the ldap options in a dict to make it easier to validate and save.
    ldap_settings = {
        'ldap_host': {'value': request.form['ldap_host'].strip(), 'error': 'LDAP Host cannot be empty'},
        'ldap_base_dn': {'value': request.form['ldap_base_dn'].strip(), 'error': 'LDAP Base cannot be empty'},
        'ldap_domain': {'value': request.form['ldap_domain'].strip(), 'error': 'LDAP Domain cannot be empty'},
        'ldap_bind_user': {'value': request.form['ldap_bind_user'].strip(), 'error': 'LDAP Bind User cannot be empty'},
        # 'ldap_bind_pass': {'value': request.form['ldap_bind_pass'].strip(),
        #                    'error': 'LDAP Bind Password cannot be empty'},
        'ldap_mapping_username': {'value': request.form['ldap_mapping_username'].strip(),
                                  'error': 'LDAP Mapping Username cannot be empty'},
        'ldap_mapping_fullname': {'value': request.form['ldap_mapping_fullname'].strip(),
                                   'error': 'LDAP Mapping Full Name cannot be empty'}
    }

    has_errors = False
    if ldap_enabled == 1:
        # If it's disabled it doesn't make sense to validate any settings.
        for key, data in ldap_settings.items():
            if len(data['value']) == 0:
                has_errors = True
                flash(data['error'], 'error')

    if has_errors:
        return redirect(url_for('admin.settings_auth'))

    settings.save('ldap_mapping_email', request.form['ldap_mapping_email'].strip())
    settings.save('allow_logins', allow_logins)
    settings.save('ldap_enabled', ldap_enabled)
    settings.save('ldap_ssl', ldap_ssl)
    for key, data in ldap_settings.items():
        settings.save(key, data['value'])

    # If the password is not '********' then save it. This is because we show that value instead of the actual password.
    if len(ldap_bind_pass) > 0 and ldap_bind_pass != '********':
        settings.save('ldap_bind_pass', ldap_bind_pass)

    # When settings are saved, run system updates.
    system = provider.system()
    system.run_updates()

    flash('Settings saved', 'success')
    return redirect(url_for('admin.settings_auth'))


@bp.route('/users', methods=['GET'])
@login_required
def users():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    users = UserModel.query.filter().order_by(UserModel.id).all()

    return render_template(
        'admin/users/index.html',
        users=users
    )


@bp.route('/users/edit/<int:user_id>', methods=['GET'])
@login_required
def user_edit(user_id):
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user = None if user_id <= 0 else UserModel.query.filter(UserModel.id == user_id).first()

    return render_template(
        'admin/users/edit.html',
        user=user
    )


@bp.route('/users/edit/<int:user_id>/save', methods=['POST'])
@login_required
def user_save(user_id):
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    username = request.form['username'].strip() if 'username' in request.form else ''
    password = request.form['password'].strip() if 'password' in request.form else ''
    full_name = request.form['full_name'].strip() if 'full_name' in request.form else ''
    email = request.form['email'].strip() if 'email' in request.form else ''
    admin = int(request.form.get('admin', 0))
    ldap = int(request.form.get('ldap', 0))
    active = int(request.form.get('active', 0))

    provider = Provider()
    users = provider.users()

    if not users.save(user_id, username, password, full_name, email, admin, ldap, active):
        flash(users.get_last_error(), 'error')
        return redirect(url_for('admin.user_edit', user_id=user_id))

    flash('User saved', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/logins', methods=['GET'])
@login_required
def logins():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    users = provider.users()
    user_logins = users.get_user_logins(0)

    return render_template(
        'admin/users/logins.html',
        logins=user_logins
    )


@bp.route('/shell/logs', methods=['GET'])
@login_required
def shell_logs():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    page = int(request.args.get('page', 1))
    if page <= 0:
        page = 1

    provider = Provider()
    shell = provider.shell()
    shell_logs = shell.get_logs(page=page, per_page=20)

    return render_template(
        'admin/shell/logs.html',
        shell_logs=shell_logs
    )


@bp.route('/system/messages', methods=['GET'])
@login_required
def system_messages():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    return render_template(
        'admin/system/messages.html'
    )


@bp.route('/system/messages/save', methods=['POST'])
@login_required
def system_messages_save():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    settings = provider.settings()

    system_message_login = request.form['system_message_login'].strip()
    system_message_login_show = int(request.form.get('system_message_login_show', 0))

    settings.save('system_message_login', system_message_login)
    settings.save('system_message_login_show', system_message_login_show)

    flash('Settings saved', 'success')
    return redirect(url_for('admin.system_messages'))


@bp.route('/', methods=['GET'])
@login_required
def index():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    return render_template(
        'admin/index.html'
    )


@bp.route('/settings/general', methods=['GET'])
@login_required
def settings_general():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    filesystem = provider.filesystem()

    themes = filesystem.get_files(os.path.join(current_app.root_path, 'static', 'css', 'themes'))

    return render_template(
        'admin/settings/general.html',
        themes=themes
    )


@bp.route('/settings/general/save', methods=['POST'])
@login_required
def settings_general_save():
    provider = Provider()
    settings = provider.settings()
    filesystem = provider.filesystem()

    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    wordlists_path = request.form['wordlists_path'].strip()
    uploaded_hashes_path = request.form['uploaded_hashes_path'].strip()
    theme = request.form['theme'].strip()
    webpush_enabled = int(request.form.get('webpush_enabled', 0))
    vapid_private = request.form['vapid_private'].strip()
    vapid_public = request.form['vapid_public'].strip()

    has_errors = False
    if len(wordlists_path) == 0 or not os.path.isdir(wordlists_path):
        has_errors = True
        flash('Wordlist directory does not exist', 'error')
    elif not os.access(wordlists_path, os.R_OK):
        has_errors = True
        flash('Wordlist directory is not readable', 'error')

    if len(uploaded_hashes_path) > 0 and not os.path.isdir(uploaded_hashes_path):
        has_errors = True
        flash('Uploaded Hashes directory does not exist', 'error')
    elif len(uploaded_hashes_path) > 0 and not os.access(uploaded_hashes_path, os.R_OK):
        has_errors = True
        flash('Uploaded Hashes directory is not readable', 'error')

    themes = filesystem.get_files(os.path.join(current_app.root_path, 'static', 'css', 'themes'))

    if not (theme + '.css') in themes:
        flash('Invalid theme', 'error')
        return redirect(url_for('admin.settings_general'))

    if has_errors:
        return redirect(url_for('admin.settings_general'))

    settings.save('wordlists_path', wordlists_path)
    settings.save('uploaded_hashes_path', uploaded_hashes_path)
    settings.save('theme', theme)
    # Only update if it's not '********' because we don't show it in the UI.
    if vapid_private != '********':
        settings.save('vapid_private', vapid_private)
    settings.save('vapid_public', vapid_public)
    settings.save('webpush_enabled', webpush_enabled)

    flash('Settings saved', 'success')
    return redirect(url_for('admin.settings_general'))
