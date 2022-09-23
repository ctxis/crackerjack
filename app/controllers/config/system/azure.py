from .. import bp
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/azure', methods=['GET'])
@login_required
@admin_required
def azure():
    provider = Provider()
    ldap = provider.ldap()

    return render_template(
        'config/system/azure.html'
    )


@bp.route('/azure/save', methods=['POST'])
@login_required
@admin_required
def azure_save():
    provider = Provider()
    settings = provider.settings()

    azure_enabled = int(request.form.get('azure_enabled', 0)) == 1
    azure_tenant_id = request.form['azure_tenant_id'].strip()
    azure_client_id = request.form['azure_client_id'].strip()
    azure_client_secret = request.form['azure_client_secret'].strip()
    if azure_client_secret == '********':
        azure_client_secret = settings.get('azure_client_secret', '')

    if azure_enabled:
        if len(azure_tenant_id) == 0 and len(azure_client_id) == 0 and len(azure_client_secret) == 0:
            flash('Please enter all required fields', 'error')
            return redirect(url_for('config.azure'))

    settings.save('azure_enabled', azure_enabled)
    settings.save('azure_tenant_id', azure_tenant_id)
    settings.save('azure_client_id', azure_client_id)
    settings.save('azure_client_secret', azure_client_secret)

    flash('Settings saved', 'success')
    return redirect(url_for('config.azure'))
