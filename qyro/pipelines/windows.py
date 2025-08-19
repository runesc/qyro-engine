from qyro._store import QYRO_INTERNAL_STATE

def build_for_windows(debug=False):

    if isinstance(debug, str):
        debug = debug.lower() in ('dev', 'development', 'true', '1')

    show_console = QYRO_INTERNAL_STATE.get_config('settings')['show_console_window']


    show_console = debug if debug is not None else show_console

    print(f"Debug mode: {debug}")
    print(f"Show console window: {show_console}")