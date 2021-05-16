from .. import bp
from flask import current_app
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


@bp.route('/api', methods=['GET'])
@login_required
def api():
    provider = Provider()
    apiman = provider.api()

    apikeys = apiman.get(current_user.id)

    return render_template(
        'config/account/api.html',
        apikeys=apikeys
    )


@bp.route('/api/add', methods=['POST'])
@login_required
def api_add():
    name = request.form['name'].strip()
    if len(name) == 0:
        flash('Please select a key name', 'error')
        return redirect(url_for('config.api'))

    provider = Provider()
    apiman = provider.api()

    if not apiman.create_key(current_user.id, name):
        flash('Could not create key', 'error')
        return redirect(url_for('config.api'))

    flash('Key created', 'success')
    return redirect(url_for('config.api'))


@bp.route('/api/set/<int:key_id>/status', methods=['POST'])
@login_required
def api_set_status(key_id):
    provider = Provider()
    apiman = provider.api()

    if not apiman.can_access(current_user, key_id):
        flash('Access denied', 'error')
        return redirect(url_for('home.index'))

    action = request.form['action'].strip()
    value = True if action == 'enable' else False

    if not apiman.set_key_status(key_id, value):
        flash('Could not set key status', 'error')
        return redirect(url_for('config.api'))

    flash('Status updated', 'success')
    return redirect(url_for('config.api'))
