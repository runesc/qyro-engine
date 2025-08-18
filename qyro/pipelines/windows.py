from qyro._store import QYRO_INTERNAL_STATE

def build_for_windows(debug=False):
    if not (debug or QYRO_INTERNAL_STATE.get_config('settings')['show_console_window']):
        print("hello")

    print(QYRO_INTERNAL_STATE.get_config('settings')['show_console_window'])