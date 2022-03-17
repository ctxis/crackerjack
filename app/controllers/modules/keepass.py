from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


@bp.route('/keepass', methods=['GET'])
@login_required
def keepass_index():
    return render_template(
        'modules/keepass/index.html',
        hash=''
    )


@bp.route('/keepass', methods=['POST'])
@login_required
def keepass_upload():
    file = request.files['document']
    if file.filename == '':
        flash('No document uploaded', 'error')
        return redirect(url_for('modules.keepass_index'))

    keepass_manager = Provider().module_keepass()
    hash = keepass_manager.extract(file)

    return render_template(
        'modules/keepass/index.html',
        hash=hash
    )
