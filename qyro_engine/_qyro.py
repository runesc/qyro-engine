from qyro_engine.utils.platform import linux_based, ubuntu_based, arch_based, fedora_based, _get_platform_name

def get_core_settings(project_dir):
    return {'project_dir': project_dir}

def get_default_profiles():
    profiles = ['base', 'secret', _get_platform_name().lower()]
    if linux_based():
        if ubuntu_based():
            profiles.append('ubuntu')
        elif arch_based():
            profiles.append('arch')
        elif fedora_based():
            profiles.append('fedora')
    return profiles


def filter_public_settings(settings):
    return {k: settings[k] for k in settings.get('public_settings', [])}