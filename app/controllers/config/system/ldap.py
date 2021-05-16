from .. import bp
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/ldap', methods=['GET'])
@login_required
@admin_required
def ldap():
    return render_template(
        'config/system/ldap.html'
    )


@bp.route('/ldap/save', methods=['POST'])
@login_required
@admin_required
def ldap_save():
    provider = Provider()
    settings = provider.settings()

    ldap_enabled = int(request.form.get('ldap_enabled', 0))
    ldap_ssl = int(request.form.get('ldap_ssl', 0))
    ldap_bind_pass = request.form['ldap_bind_pass'].strip()

    # Put the rest of the ldap options in a dict to make it easier to validate and save.
    ldap_settings = {
        'ldap_host': {'value': request.form['ldap_host'].strip(), 'error': 'LDAP Host cannot be empty'},
        'ldap_base_dn': {'value': request.form['ldap_base_dn'].strip(), 'error': 'LDAP Base cannot be empty'},
        'ldap_domain': {'value': request.form['ldap_domain'].strip(), 'error': 'LDAP Domain cannot be empty'},
        'ldap_bind_user': {'value': request.form['ldap_bind_user'].strip(), 'error': 'LDAP Bind User cannot be empty'},
        'ldap_mapping_username': {'value': request.form['ldap_mapping_username'].strip(),
                                  'error': 'LDAP Mapping Username cannot be empty'},
        'ldap_mapping_fullname': {'value': request.form['ldap_mapping_fullname'].strip(),
                                  'error': 'LDAP Mapping Full Name cannot be empty'}
    }

    has_errors = False
    if ldap_enabled == 1:
        # If it's disabled it doesn't make sense to validate any settings.
        for key, data in ldap_settings.items():
            if len(data['value']) == 0:
                has_errors = True
                flash(data['error'], 'error')

    if has_errors:
        return redirect(url_for('config.ldap'))

    settings.save('ldap_mapping_email', request.form['ldap_mapping_email'].strip())
    settings.save('ldap_enabled', ldap_enabled)
    settings.save('ldap_ssl', ldap_ssl)
    for key, data in ldap_settings.items():
        settings.save(key, data['value'])

    # If the password is not '********' then save it. This is because we show that value instead of the actual password.
    if len(ldap_bind_pass) > 0 and ldap_bind_pass != '********':
        settings.save('ldap_bind_pass', ldap_bind_pass)

    # When settings are saved, run system updates.
    system = provider.system()
    system.run_updates()

    flash('Settings saved', 'success')
    return redirect(url_for('config.ldap'))
