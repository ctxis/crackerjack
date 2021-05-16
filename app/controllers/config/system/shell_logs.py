from .. import bp
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/logs/shell', methods=['GET'])
@login_required
@admin_required
def shell_logs():
    page = int(request.args.get('page', 1))
    if page <= 0:
        page = 1

    provider = Provider()
    shell = provider.shell()
    shell_logs = shell.get_logs(page=page, per_page=20)

    return render_template(
        'config/system/shell_logs.html',
        shell_logs=shell_logs
    )
