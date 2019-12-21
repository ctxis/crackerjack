from flask import Blueprint, current_app
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
import os


bp = Blueprint('account', __name__)


@bp.route('/<int:user_id>', methods=['GET'])
@login_required
def index(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    elif current_user.id != user_id:
        flash('Access denied', 'error');
        return redirect(url_for('home.index'))

    provider = Provider()
    users = provider.users()

    user = users.get_by_id(current_user.id)

    return render_template(
        'account/index.html',
        user=user
    )


@bp.route('/<int:user_id>/password', methods=['GET'])
@login_required
def password(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    elif current_user.id != user_id:
        flash('Access denied', 'error')
        return redirect(url_for('home.index'))

    return 'password'


@bp.route('/<int:user_id>/theme', methods=['GET'])
@login_required
def theme(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    elif current_user.id != user_id:
        flash('Access denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    users = provider.users()
    filesystem = provider.filesystem()
    user_settings = provider.user_settings()

    user = users.get_by_id(current_user.id)
    themes = filesystem.get_files(os.path.join(current_app.root_path, 'static', 'css', 'themes'))
    theme = user_settings.get(user_id, 'theme', 'lumen')

    return render_template(
        'account/theme.html',
        user=user,
        themes=themes,
        selected_theme=theme
    )


@bp.route('/<int:user_id>/theme/save', methods=['POST'])
@login_required
def theme_save(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    elif current_user.id != user_id:
        flash('Access denied', 'error')
        return redirect(url_for('home.index'))

    theme = request.form['theme'].strip()

    provider = Provider()
    filesystem = provider.filesystem()
    user_settings = provider.user_settings()

    themes = filesystem.get_files(os.path.join(current_app.root_path, 'static', 'css', 'themes'))

    if not (theme + '.css') in themes:
        flash('Invalid theme', 'error')
        return redirect(url_for('account.theme', user_id=user_id))

    user_settings.save(user_id, 'theme', theme)

    flash('Theme saved. To make sure everything is working, please force-refresh the page (CTRL-F5)', 'success')
    return redirect(url_for('account.theme', user_id=user_id))
