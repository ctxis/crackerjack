from .. import bp
from flask import current_app
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
import os
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/hashcat', methods=['GET'])
@login_required
@admin_required
def hashcat():
    return render_template(
        'config/system/hashcat.html',
    )


@bp.route('/hashcat/save', methods=['POST'])
@login_required
@admin_required
def hashcat_save():
    provider = Provider()
    settings = provider.settings()

    hashcat_binary = request.form['hashcat_binary'].strip()
    hashcat_rules_path = request.form['hashcat_rules_path'].strip()
    hashcat_status_interval = request.form['hashcat_status_interval'].strip()
    hashcat_force = int(request.form.get('hashcat_force', 0))
    wordlists_path = request.form['wordlists_path'].strip()
    uploaded_hashes_path = request.form['uploaded_hashes_path'].strip()

    has_errors = False
    # Validate wordlist
    if len(wordlists_path) == 0 or not os.path.isdir(wordlists_path):
        has_errors = True
        flash('Wordlist directory does not exist', 'error')
    elif not os.access(wordlists_path, os.R_OK):
        has_errors = True
        flash('Wordlist directory is not readable', 'error')

    # Validate uploaded hash path
    if len(uploaded_hashes_path) > 0 and not os.path.isdir(uploaded_hashes_path):
        has_errors = True
        flash('Uploaded Hashes directory does not exist', 'error')
    elif len(uploaded_hashes_path) > 0 and not os.access(uploaded_hashes_path, os.R_OK):
        has_errors = True
        flash('Uploaded Hashes directory is not readable', 'error')

    # Validate executable
    if len(hashcat_binary) == 0 or not os.path.isfile(hashcat_binary):
        has_errors = True
        flash('Hashcat executable does not exist', 'error')
    elif not os.access(hashcat_binary, os.X_OK):
        has_errors = True
        flash('Hashcat file is not executable', 'error')

    # Validate rules
    if len(hashcat_rules_path) == 0 or not os.path.isdir(hashcat_rules_path):
        has_errors = True
        flash('Hashcat rules directory does not exist', 'error')
    elif not os.access(hashcat_rules_path, os.R_OK):
        has_errors = True
        flash('Hashcat rules directory is not readable', 'error')

    # Validate interval
    if len(hashcat_status_interval) == 0:
        has_errors = True
        flash('Hashcat Status Interval must be set', 'error')

    if has_errors:
        return redirect(url_for('config.hashcat'))

    hashcat_status_interval = int(hashcat_status_interval)
    if hashcat_status_interval <= 0:
        hashcat_status_interval = 10

    settings.save('hashcat_binary', hashcat_binary)
    settings.save('hashcat_rules_path', hashcat_rules_path)
    settings.save('hashcat_status_interval', hashcat_status_interval)
    settings.save('hashcat_force', hashcat_force)
    settings.save('wordlists_path', wordlists_path)
    settings.save('uploaded_hashes_path', uploaded_hashes_path)

    flash('Settings saved', 'success')
    return redirect(url_for('config.hashcat'))
