from .. import bp
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/messages', methods=['GET'])
@login_required
@admin_required
def messages():
    return render_template(
        'config/system/messages.html'
    )


@bp.route('/messages/save', methods=['POST'])
@login_required
@admin_required
def messages_save():
    provider = Provider()
    settings = provider.settings()

    system_message_login = request.form['system_message_login'].strip()
    system_message_login_show = int(request.form.get('system_message_login_show', 0))

    settings.save('system_message_login', system_message_login)
    settings.save('system_message_login_show', system_message_login_show)

    flash('Settings saved', 'success')
    return redirect(url_for('config.messages'))
