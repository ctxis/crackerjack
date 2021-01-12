from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


@bp.route('/office', methods=['GET'])
@login_required
def office_index():
    return render_template(
        'modules/office/index.html',
        hash=''
    )


@bp.route('/office', methods=['POST'])
@login_required
def office_upload():
    file = request.files['document']
    if file.filename == '':
        flash('No document uploaded', 'error')
        return redirect(url_for('modules.office_index'))

    office_manager = Provider().module_office()
    hash = office_manager.extract(file)

    return render_template(
        'modules/office/index.html',
        hash=hash
    )
