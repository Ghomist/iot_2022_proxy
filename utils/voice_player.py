import os
from config import voice_vol_base, voice_path, voice_list


def _get_voice_(v) -> str:
    return os.path.join(voice_path, voice_list[v])


def on_beep():
    os.system(f"mplayer -af volume={voice_vol_base+40} {_get_voice_('beep')} -quiet > /dev/null")  # 2>&1


def on_warning():
    os.system(f"mplayer -af volume={voice_vol_base+40} {_get_voice_('warning')} -quiet > /dev/null")


def on_info():
    os.system(f"mplayer -af volume={voice_vol_base+5} {_get_voice_('info')} -quiet > /dev/null")
