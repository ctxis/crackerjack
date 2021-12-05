from .. import bp
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/device_profiles', methods=['GET'])
@login_required
@admin_required
def device_profiles():
    provider = Provider()
    device_profile_manager = provider.device_profiles()

    return render_template(
        'config/system/device_profiles/index.html',
        supported_devices=device_profile_manager.get_supported_devices(),
        profiles=device_profile_manager.get_device_profiles()
    )


@bp.route('/device_profiles/<int:id>/edit', methods=['GET'])
@login_required
@admin_required
def device_profile_edit(id):
    provider = Provider()
    device_profile_manager = provider.device_profiles()

    return render_template(
        'config/system/device_profiles/edit.html',
        supported_devices=device_profile_manager.get_supported_devices(),
        profile=device_profile_manager.get_profile(id)
    )


@bp.route('/device_profiles/<int:id>/save', methods=['POST'])
@login_required
@admin_required
def device_profile_save(id):
    provider = Provider()
    device_profile_manager = provider.device_profiles()

    name = request.form['name'].strip() if 'name' in request.form else ''
    enabled = True if 'enabled' in request.form else False
    devices = request.form.getlist('devices', int)

    if len(name) == 0:
        flash('Profile name cannot be empty', 'error')
        return redirect(url_for('config.device_profile_edit', id=id))
    elif len(devices) == 0:
        flash('Please select at least one device', 'error')
        return redirect(url_for('config.device_profile_edit', id=id))

    for device_id in devices:
        if not device_profile_manager.is_valid_device(device_id):
            flash('Invalid device selected', 'error')
            return redirect(url_for('config.device_profile_edit', id=id))

    profile = device_profile_manager.save(id, name, devices, enabled)
    if not profile:
        flash('Could not save profile', 'error')
        return redirect(url_for('config.device_profile_edit', id=id))

    flash('Device profile created', 'success')
    return redirect(url_for('config.device_profiles'))


@bp.route('/device_profiles/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def device_profile_delete(id):
    provider = Provider()
    device_profile_manager = provider.device_profiles()

    device_profile_manager.delete(id)
    flash('Device profile deleted', 'success')
    return redirect(url_for('config.device_profiles'))


