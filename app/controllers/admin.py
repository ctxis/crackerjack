from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
import os
from app.lib.base.provider import Provider


bp = Blueprint('admin', __name__)


@bp.route('/settings/hashcat', methods=['GET'])
@login_required
def settings_hashcat():
    if not current_user.admin:
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    settings = provider.settings()

    return render_template(
        'admin/settings/hashcat.html',
        settings={
            'hashcat_binary': settings.get('hashcat_binary', ''),
            'wordlists_path': settings.get('wordlists_path', ''),
            'hashcat_rules_path': settings.get('hashcat_rules_path', '')
        }
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
    wordlists_path = request.form['wordlists_path'].strip()
    hashcat_rules_path = request.form['hashcat_rules_path'].strip()

    has_errors = False
    if len(hashcat_binary) == 0 or not os.path.isfile(hashcat_binary):
        has_errors = True
        flash('Hashcat executable does not exist', 'error')
    elif not os.access(hashcat_binary, os.X_OK):
        has_errors = True
        flash('Hashcat file is not executable', 'error')

    if len(wordlists_path) == 0 or not os.path.isdir(wordlists_path):
        has_errors = True
        flash('Wordlist directory does not exist', 'error')
    elif not os.access(wordlists_path, os.R_OK):
        has_errors = True
        flash('Wordlist directory is not readable', 'error')

    if len(hashcat_rules_path) == 0 or not os.path.isdir(hashcat_rules_path):
        has_errors = True
        flash('Hashcat rules directory does not exist', 'error')
    elif not os.access(hashcat_rules_path, os.R_OK):
        has_errors = True
        flash('Hashcat rules directory is not readable', 'error')

    if has_errors:
        return redirect(url_for('admin.settings_hashcat'))

    settings.save('hashcat_binary', hashcat_binary)
    settings.save('wordlists_path', wordlists_path)
    settings.save('hashcat_rules_path', hashcat_rules_path)

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
    settings = provider.settings()

    return render_template(
        'admin/settings/auth.html',
        settings={
            'allow_logins': settings.get('allow_logins', 0)
        }
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

    settings.save('allow_logins', allow_logins)

    # When settings are saved, run system updates.
    system = provider.system()
    system.run_updates()

    flash('Settings saved', 'success')
    return redirect(url_for('admin.settings_auth'))
