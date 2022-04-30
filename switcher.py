import argparse
import configparser
import sys
from functools import partial
from logging import Logger
from tkinter import messagebox

import pyWinCoreAudio
from _weakref import ReferenceType
from pyWinCoreAudio import ON_ENDPOINT_DEFAULT_CHANGED
from pyWinCoreAudio.mmdeviceapi import Device, EDataFlow, ERole, IMMDevice, IMMDeviceEnumerator


def on_endpoint_default_changed(signal, device: Device, endpoint, role: ERole, flow: EDataFlow, logger: Logger):
    assert device.name is not None
    logger.debug("Default changed:", device.name + "." + endpoint.name, "role:", role, "flow:", flow)


def switch_speaker(primary_device_guid: str, secondary_device_guid: str, logger: Logger):
    _on_endpoint_default_changed = ON_ENDPOINT_DEFAULT_CHANGED.register(
        partial(on_endpoint_default_changed, logger=logger)
    )

    default_endpoint: IMMDevice | None = IMMDeviceEnumerator().default_audio_endpoint(
        EDataFlow.eRender, ERole.eConsole
    )
    assert default_endpoint is not None
    target_guid = secondary_device_guid if default_endpoint.guid == primary_device_guid else primary_device_guid

    devices_ref: ReferenceType[IMMDeviceEnumerator] = pyWinCoreAudio.devices(False)
    devices = devices_ref()
    assert devices is not None
    for device in devices:
        device: Device
        for endpoint in device:
            endpoint: IMMDevice
            if endpoint.guid == target_guid:
                endpoint.set_default(True)
                break
        else:
            continue
        break
    else:
        messagebox.showinfo("Warning", "Target deveice was not found. \n(uuid: {})".format(target_guid))

    _on_endpoint_default_changed.unregister()
    pyWinCoreAudio.stop()


def init_config(config: configparser.ConfigParser, logger: Logger):
    logger.debug("check config sections and options.")
    if not config.has_section("RENDER_DEVICE_GUID"):
        logger.exception('does not exists "RENDER_DEVICE_GUID"')
        raise ValueError('does not exists "RENDER_DEVICE_GUID"')
    if not config.has_option("RENDER_DEVICE_GUID", "PRIMARY_DEVICE"):
        logger.exception('does not exists "RENDER_DEVICE_GUID.PRIMARY_DEVICE"')
        raise ValueError('does not exists "RENDER_DEVICE_GUID.PRIMARY_DEVICE"')
    if not config.has_option("RENDER_DEVICE_GUID", "SECONDARY_DEVICE"):
        logger.exception('does not exists "RENDER_DEVICE_GUID.SECONDARY_DEVICE"')
        raise ValueError('does not exists "RENDER_DEVICE_GUID.SECONDARY_DEVICE"')


def get_my_logger():
    from logging import DEBUG, StreamHandler, getLogger

    logger = getLogger(__name__)
    logger.setLevel(DEBUG)
    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    logger.addHandler(stream_handler)
    return logger


def main(args):
    logger = get_my_logger()

    parser = configparser.ConfigParser()
    parser.read(args.config_file, encoding="utf-8")
    try:
        init_config(parser, logger)
    except ValueError:
        messagebox.showinfo("Does not exitst Config file", "First, create config.ini by config_editor.exe")
        sys.exit(1)

    primary_device_guid = parser["RENDER_DEVICE_GUID"]["PRIMARY_DEVICE"]
    secondary_device_guid = parser["RENDER_DEVICE_GUID"]["SECONDARY_DEVICE"]

    switch_speaker(primary_device_guid=primary_device_guid, secondary_device_guid=secondary_device_guid, logger=logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args)
