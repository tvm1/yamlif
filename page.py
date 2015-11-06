# This is example file that processes some values from general_setup page
# when user saves the page. A string can be returned back to UI and will be
# viewable as popup.


def general_setup_validator(values):

    log = ""

    if values['sys_v_ipc'] is True:
        values['sys_v_ipc'] = False
        log += "Changed SYS_V_IPC to False. "

    if int(values['kernel_log_buffer']) > 32:
        values['kernel_log_buffer'] = 1
        log += "Changed kernel_log_buffer to 1, because it was larger than 32. "

    if not str(values['cpu_kernel_log_buffer']).isdigit():
        values['cpu_kernel_log_buffer'] = 64
        log += "Changed cpu_kernel_log_buffer to 64, because it was not number."

    return log
