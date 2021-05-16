from .. import bp
from flask import current_app
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
import os
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/general', methods=['GET'])
@login_required
@admin_required
def general():
    provider = Provider()
    filesystem = provider.filesystem()

    themes = filesystem.get_files(os.path.join(current_app.root_path, 'static', 'css', 'themes'))

    return render_template(
        'config/system/general.html',
        themes=themes
    )


@bp.route('/general/save', methods=['POST'])
@login_required
@admin_required
def general_save():
    provider = Provider()
    settings = provider.settings()
    filesystem = provider.filesystem()

    theme = request.form['theme'].strip()
    themes = filesystem.get_files(os.path.join(current_app.root_path, 'static', 'css', 'themes'))

    if not (theme + '.css') in themes:
        flash('Invalid theme', 'error')
        return redirect(url_for('config.general'))

    settings.save('theme', theme)
    flash('Settings saved', 'success')
    return redirect(url_for('config.general'))
