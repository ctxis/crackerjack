from .. import bp
from flask import current_app
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
import os


@bp.route('/theme', methods=['GET'])
@login_required
def theme():
    provider = Provider()
    users = provider.users()
    filesystem = provider.filesystem()
    user_settings = provider.user_settings()
    settings = provider.settings()

    user = users.get_by_id(current_user.id)
    themes = filesystem.get_files(os.path.join(current_app.root_path, 'static', 'css', 'themes'))
    theme = user_settings.get(current_user.id, 'theme', settings.get('theme', 'lumen'))

    return render_template(
        'config/account/theme.html',
        user=user,
        themes=themes,
        selected_theme=theme
    )


@bp.route('/theme/save', methods=['POST'])
@login_required
def theme_save():
    theme = request.form['theme'].strip()

    provider = Provider()
    filesystem = provider.filesystem()
    user_settings = provider.user_settings()

    themes = filesystem.get_files(os.path.join(current_app.root_path, 'static', 'css', 'themes'))

    if not (theme + '.css') in themes:
        flash('Invalid theme', 'error')
        return redirect(url_for('config.theme', user_id=current_user.id))

    user_settings.save(current_user.id, 'theme', theme)

    flash('Theme saved. To make sure everything is working, please force-refresh the page (CTRL-F5)', 'success')
    return redirect(url_for('config.theme', user_id=current_user.id))
