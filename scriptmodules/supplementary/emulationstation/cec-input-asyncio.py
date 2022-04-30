#!/usr/bin/env python3

import argparse
import asyncio
import logging
import re
from calendar import c

import evdev
import uinput

logging.basicConfig(
    format="[%(asctime)s.%(msecs)03d][%(levelname)8s][%(module)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

RETROARCH_CONFIG_KEY_BY_CEC_KEY = {
    "yellow": "input_player1_select",
    "blue": "input_player1_start",
    "left": "input_player1_left",
    "right": "input_player1_right",
    "up": "input_player1_up",
    "down": "input_player1_down",
    "select": "input_player1_a",
    "exit": "input_player1_b",
    "backward": "input_player1_a",
    "play": "input_player1_b",
    "pause": "input_player1_x",
    "forward": "input_player1_y",
}

RETROARCH_KEY_BY_CEC_KEY = {
    "red": "f2",
}


def get_args():
    parser = argparse.ArgumentParser(description="Description goes here.")
    parser.add_argument(
        "-v", dest="verbose_info", action="store_true", help="Enable info messages."
    )
    parser.add_argument(
        "-vv",
        dest="verbose_debug",
        action="store_true",
        help="Enable info and debug messages.",
    )
    args = parser.parse_args()

    if args.verbose_debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose_info:
        logging.getLogger().setLevel(logging.INFO)

    return args


def get_uinput_key_by_retroarch_key():
    """Map ES supported keys to python-uinput keys"""

    keymap = {
        "left": evdev.ecodes.KEY_LEFT,
        "right": evdev.ecodes.KEY_RIGHT,
        "up": evdev.ecodes.KEY_UP,
        "down": evdev.ecodes.KEY_DOWN,
        "enter": evdev.ecodes.KEY_ENTER,
        "kp_enter": evdev.ecodes.KEY_KPENTER,
        "tab": evdev.ecodes.KEY_TAB,
        "insert": evdev.ecodes.KEY_INSERT,
        "del": evdev.ecodes.KEY_DELETE,
        "end": evdev.ecodes.KEY_END,
        "home": evdev.ecodes.KEY_HOME,
        "rshift": evdev.ecodes.KEY_RIGHTSHIFT,
        "shift": evdev.ecodes.KEY_LEFTSHIFT,
        "rctrl": evdev.ecodes.KEY_RIGHTCTRL,
        "ctrl": evdev.ecodes.KEY_LEFTCTRL,
        "ralt": evdev.ecodes.KEY_RIGHTALT,
        "alt": evdev.ecodes.KEY_LEFTALT,
        "space": evdev.ecodes.KEY_SPACE,
        "escape": evdev.ecodes.KEY_ESC,
        "kp_minus": evdev.ecodes.KEY_KPMINUS,
        "kp_plus": evdev.ecodes.KEY_KPPLUS,
        "f1": evdev.ecodes.KEY_F1,
        "f2": evdev.ecodes.KEY_F2,
        "f3": evdev.ecodes.KEY_F3,
        "f4": evdev.ecodes.KEY_F4,
        "f5": evdev.ecodes.KEY_F5,
        "f6": evdev.ecodes.KEY_F6,
        "f7": evdev.ecodes.KEY_F7,
        "f8": evdev.ecodes.KEY_F8,
        "f9": evdev.ecodes.KEY_F9,
        "f10": evdev.ecodes.KEY_F10,
        "f11": evdev.ecodes.KEY_F11,
        "f12": evdev.ecodes.KEY_F12,
        "num1": evdev.ecodes.KEY_1,
        "num2": evdev.ecodes.KEY_2,
        "num3": evdev.ecodes.KEY_3,
        "num4": evdev.ecodes.KEY_4,
        "num5": evdev.ecodes.KEY_5,
        "num6": evdev.ecodes.KEY_6,
        "num7": evdev.ecodes.KEY_7,
        "num8": evdev.ecodes.KEY_8,
        "num9": evdev.ecodes.KEY_9,
        "num0": evdev.ecodes.KEY_0,
        "pageup": evdev.ecodes.KEY_PAGEUP,
        "pagedown": evdev.ecodes.KEY_PAGEDOWN,
        "keypad1": evdev.ecodes.KEY_KP1,
        "keypad2": evdev.ecodes.KEY_KP2,
        "keypad3": evdev.ecodes.KEY_KP3,
        "keypad4": evdev.ecodes.KEY_KP4,
        "keypad5": evdev.ecodes.KEY_KP5,
        "keypad6": evdev.ecodes.KEY_KP6,
        "keypad7": evdev.ecodes.KEY_KP7,
        "keypad8": evdev.ecodes.KEY_KP8,
        "keypad9": evdev.ecodes.KEY_KP9,
        "keypad0": evdev.ecodes.KEY_KP0,
        "period": evdev.ecodes.KEY_DOT,
        "capslock": evdev.ecodes.KEY_CAPSLOCK,
        "numlock": evdev.ecodes.KEY_NUMLOCK,
        "backspace": evdev.ecodes.KEY_BACKSPACE,
        "pause": evdev.ecodes.KEY_PAUSE,
        "scrolllock": evdev.ecodes.KEY_SCROLLLOCK,
        "backquote": evdev.ecodes.KEY_GRAVE,
        "comma": evdev.ecodes.KEY_COMMA,
        "minus": evdev.ecodes.KEY_MINUS,
        "slash": evdev.ecodes.KEY_SLASH,
        "semicolon": evdev.ecodes.KEY_SEMICOLON,
        "equals": evdev.ecodes.KEY_EQUAL,
        "backslash": evdev.ecodes.KEY_BACKSLASH,
        "kp_period": evdev.ecodes.KEY_KPDOT,
        "kp_equals": evdev.ecodes.KEY_KPEQUAL,
        "a": evdev.ecodes.KEY_A,
        "b": evdev.ecodes.KEY_B,
        "c": evdev.ecodes.KEY_C,
        "d": evdev.ecodes.KEY_D,
        "e": evdev.ecodes.KEY_E,
        "f": evdev.ecodes.KEY_F,
        "g": evdev.ecodes.KEY_G,
        "h": evdev.ecodes.KEY_H,
        "i": evdev.ecodes.KEY_I,
        "j": evdev.ecodes.KEY_J,
        "k": evdev.ecodes.KEY_K,
        "l": evdev.ecodes.KEY_L,
        "m": evdev.ecodes.KEY_M,
        "n": evdev.ecodes.KEY_N,
        "o": evdev.ecodes.KEY_O,
        "p": evdev.ecodes.KEY_P,
        "q": evdev.ecodes.KEY_Q,
        "r": evdev.ecodes.KEY_R,
        "s": evdev.ecodes.KEY_S,
        "t": evdev.ecodes.KEY_T,
        "u": evdev.ecodes.KEY_U,
        "v": evdev.ecodes.KEY_V,
        "w": evdev.ecodes.KEY_W,
        "x": evdev.ecodes.KEY_X,
        "y": evdev.ecodes.KEY_Y,
        "z": evdev.ecodes.KEY_Z,
    }

    return keymap


def press_or_release_key_for_cec_debug_line(
    evdev_ui,
    line,
    uinput_key_by_retroarch_config_key,
    uinput_key_by_retroarch_key,
    press=True,
):
    for cec_key, retroarch_config_key in RETROARCH_CONFIG_KEY_BY_CEC_KEY.items():
        if cec_key in line:
            logger.info('Pressed %s, sending retroarch key: %s', cec_key, retroarch_config_key)
            evdev_ui.write(
                evdev.ecodes.EV_KEY,
                uinput_key_by_retroarch_config_key[retroarch_config_key],
                int(press),
            )
            evdev_ui.syn()
            return
    for cec_key, retroarch_key in RETROARCH_KEY_BY_CEC_KEY.items():
        if cec_key in line:
            logger.info('Released %s, sending retroarch key: %s', cec_key, retroarch_key)
            evdev_ui.write(
                evdev.ecodes.EV_KEY,
                uinput_key_by_retroarch_key[retroarch_key],
                int(press),
            )
            evdev_ui.syn()
            return


def get_uinput_key_by_retroarch_config_key():
    """generate a list of keys we actually need
    this will be stored in memory and will comprise of
    a,b,x,y,start,select,l,r,left,right,up,down,l2,r2,l3,r3
    keyboard corresponding values the user has chosen
    in the retroarch.cfg file"""

    uinput_key_by_retroarch_config_key = {}
    retroarch_config = read_retroarch_input_config(
        "/opt/retropie/configs/all/retroarch.cfg"
    )
    logger.debug(
        "retroarch.cfg \n%s", "\n".join(f"{k}={v}" for k, v in retroarch_config.items())
    )
    uinput_key_by_retroarch_key = get_uinput_key_by_retroarch_key()
    errors = []
    for retroarch_config_key, retroarch_config_value in retroarch_config.items():
        try:
            uinput_key = uinput_key_by_retroarch_key[retroarch_config_value]
            uinput_key_by_retroarch_config_key[retroarch_config_key] = uinput_key
        except KeyError as e:
            errors.append(e)

    if len(errors) > 0:
        logger.error(
            "The %s keys in your retroarch.cfg are unsupported\
            by this script.\nSupported keys are:\n%s",
            errors,
            get_uinput_key_by_retroarch_key().keys(),
        )
        raise RuntimeError()

    return uinput_key_by_retroarch_config_key


def read_retroarch_config(path):
    retroarch_cfg_regex = r'^\s*(\w+)\s*=\s*"?(.+?)"?$'
    config = {}
    with open(path, "r") as fp:
        for match in re.finditer(retroarch_cfg_regex, fp.read(), flags=re.MULTILINE):
            config[match.group(1)] = match.group(2)
    return config


def read_retroarch_input_config(path):
    return {
        k: v
        for k, v in read_retroarch_config(path).items()
        if k.startswith("input_player")
    }


def register_device(uinput_key_by_retroarch_config_key):
    uinput.Device([])
    return evdev.UInput()


def press_keys(
    line, evdev_uinput, uinput_key_by_retroarch_config_key, uinput_key_by_retroarch_key
):
    """Emulate keyboard presses when a mapped button on the remote control
    has been pressed.

    To navigate ES, only a,b,start,select,up,down,left,and right are required
    """

    # check for key released as pressed was displaying duplicate
    # presses on the remote control used for development
    # logger.getChild('cec-client').debug(line)

    {
        # OK button released
        "A": "01:8b:00",
        # exit button
        "B": "01:8b:0d",
        "up": "01:8b:01",
        "down": "01:8b:02",
        "left": "01:8b:03",
        "right": "01:8b:04",
        # blue button released
        "start": "01:8b:71",
        # yellow button released
        "select": "01:8b:74",
    }
    if "pressed" in line:
        logger.debug(line)
        press_or_release_key_for_cec_debug_line(
            evdev_uinput,
            line,
            uinput_key_by_retroarch_config_key,
            uinput_key_by_retroarch_key,
            press=True,
        )

    if "released" in line:
        logger.debug(line)
        press_or_release_key_for_cec_debug_line(
            evdev_uinput,
            line,
            uinput_key_by_retroarch_config_key,
            uinput_key_by_retroarch_key,
            press=False,
        )


async def read_stream(stream, cb):
    while True:
        line = await stream.readline()
        if line:
            cb(line.decode("utf-8"))
        else:
            break


async def write_stream(stream, cb):
    async for line in cb():
        logger.info('Sending command "%s" throug stdin', line)
        stream.write(line.encode("utf-8"))


async def stream_subprocess(cmd, stdin_cb, stdout_cb, stderr_cb):
    logger.info('Starting asyncio subprocess "%s" ...', " ".join(cmd))
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    await asyncio.wait(
        [
            asyncio.create_task(write_stream(process.stdin, stdin_cb)),
            asyncio.create_task(read_stream(process.stdout, stdout_cb)),
            asyncio.create_task(read_stream(process.stderr, stderr_cb)),
        ]
    )
    return await process.wait()


def execute(cmd, stdin_cb, stdout_cb, stderr_cb):
    logger.debug("Starting asyncio loop...")
    try:
        asyncio.run(
            stream_subprocess(
                cmd,
                stdin_cb,
                stdout_cb,
                stderr_cb,
            )
        )
    except KeyboardInterrupt:
        logger.info("Exited.")


def main():
    args = get_args()
    uinput_key_by_retroarch_key = get_uinput_key_by_retroarch_key()
    uinput_key_by_retroarch_config_key = get_uinput_key_by_retroarch_config_key()
    logger.debug(
        "uinput_key_by_retroarch_config_key: %s", uinput_key_by_retroarch_config_key
    )
    logger.debug("Registering device...")
    device = register_device(uinput_key_by_retroarch_config_key)
    logger.debug("Device registered %s", device)

    logger.info("Runnning cec-client...")

    def cec_client_line_callback(line):
        press_keys(
            line,
            device,
            uinput_key_by_retroarch_config_key,
            uinput_key_by_retroarch_key,
        )

    async def cec_client_input_callback():
        await asyncio.sleep(3)
        logger.info("Turning on TV")
        yield "on 0"

        await asyncio.sleep(3)
        # set self as the ACTIVE source
        logger.info("Set ourself as ACTIVE source")
        yield "as"

    execute(
        ["cec-client", "RPI", "--osd-name", "Retropie"],
        cec_client_input_callback,
        cec_client_line_callback,
        logger.error,
    )


if __name__ == "__main__":
    main()
