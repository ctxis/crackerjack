from .. import bp
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/webpush', methods=['GET'])
@login_required
@admin_required
def webpush():
    return render_template(
        'config/system/webpush.html'
    )


@bp.route('/webpush/save', methods=['POST'])
@login_required
@admin_required
def webpush_save():
    provider = Provider()
    settings = provider.settings()

    webpush_enabled = int(request.form.get('webpush_enabled', 0))
    vapid_private = request.form['vapid_private'].strip()
    vapid_public = request.form['vapid_public'].strip()

    if vapid_private != '********':
        settings.save('vapid_private', vapid_private)
    settings.save('vapid_public', vapid_public)
    settings.save('webpush_enabled', webpush_enabled)

    flash('Settings saved', 'success')
    return redirect(url_for('config.webpush'))
