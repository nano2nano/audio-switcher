import configparser
import tkinter as tk
from functools import partial
from logging import Logger, StreamHandler, getLogger
from tkinter import StringVar, ttk
from weakref import ReferenceType

import pyWinCoreAudio
from pyWinCoreAudio.mmdeviceapi import Device, EDataFlow, IMMDevice, IMMDeviceEnumerator


class MyRenderDevice:
    def __init__(self) -> None:
        render_device_names_tmp: list[str] = []
        render_device_guids_tmp: list[str] = []
        for name, guid in self.__get_sound_devices():
            render_device_names_tmp.append(name)
            render_device_guids_tmp.append(str(guid))
        self.__render_device_names: tuple[str] = tuple(render_device_names_tmp)
        self.__render_device_guids: tuple[str] = tuple(render_device_guids_tmp)
        assert len(self.__render_device_guids) == len(set(self.__render_device_guids))
        assert len(self.__render_device_names) == len(self.__render_device_guids)

    def __get_sound_devices(self):
        devices_ref: ReferenceType[IMMDeviceEnumerator] = pyWinCoreAudio.devices(False)
        devices = devices_ref()
        assert devices is not None
        for device in devices:
            device: Device
            for endpoint in device:
                endpoint: IMMDevice
                if endpoint.data_flow == EDataFlow.eRender:
                    yield endpoint.name, endpoint.guid
        pyWinCoreAudio.stop()

    def __getitem__(self, index: int):
        return {
            "name": self.__render_device_names[index],
            "guid": self.__render_device_guids[index],
        }

    @property
    def device_num(self) -> int:
        return len(self.device_guids)

    @property
    def device_names(self) -> tuple[str]:
        return self.__render_device_names

    @property
    def device_guids(self) -> tuple[str]:
        return self.__render_device_guids

    def get_index_by_guid(self, guid: str, default: int | None = None) -> int | None:
        if guid in self.__render_device_guids:
            return self.__render_device_guids.index(guid)
        else:
            return default


def save(config: configparser.ConfigParser, logger: Logger):
    logger.debug("save config...")
    with open("config.ini", "w") as f:
        config.write(f)
    logger.debug("config was saved.")


def init_config(config: configparser.ConfigParser, logger: Logger):
    logger.debug("check config sections and options.")
    if not config.has_section("RENDER_DEVICE_GUID"):
        logger.debug('does not exists "RENDER_DEVICE_GUID"')
        config.add_section("RENDER_DEVICE_GUID")
    if not config.has_option("RENDER_DEVICE_GUID", "PRIMARY_DEVICE"):
        logger.debug('does not exists "RENDER_DEVICE_GUID.PRIMARY_DEVICE"')
        config["RENDER_DEVICE_GUID"]["PRIMARY_DEVICE"] = ""
    if not config.has_option("RENDER_DEVICE_GUID", "SECONDARY_DEVICE"):
        logger.debug('does not exists "RENDER_DEVICE_GUID.SECONDARY_DEVICE"')
        config["RENDER_DEVICE_GUID"]["SECONDARY_DEVICE"] = ""


from logging import DEBUG


def main():
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)
    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    logger.addHandler(stream_handler)

    logger.debug("load config...")
    config_ini = configparser.ConfigParser()
    config_ini.read("config.ini", encoding="utf-8")
    init_config(config_ini, logger)

    logger.debug("fetch default config value...")
    default_primary_device_guid = config_ini["RENDER_DEVICE_GUID"]["PRIMARY_DEVICE"]
    default_secondary_device_guid = config_ini["RENDER_DEVICE_GUID"]["SECONDARY_DEVICE"]

    logger.debug("load my render devices...")
    my_render_device = MyRenderDevice()
    render_device_names = my_render_device.device_names
    render_device_guids = my_render_device.device_guids
    max_char = min(max([len(x) for x in render_device_guids]), 50)
    logger.debug(f'max device name length is "{max([len(x) for x in render_device_names])}"')
    logger.debug(f"if lenght longer than 50 then max_char set to 50.")

    root = tk.Tk()
    root.title("Audio Switcher ( Config editor )")
    frm = ttk.Frame(root, padding=10)
    frm.grid()

    ttk.Label(frm, text="Primary Device").grid(row=0, column=0)
    ttk.Label(frm, text="Secondary Device").grid(row=0, column=1)

    pcbValue = StringVar()
    scbValue = StringVar()
    primary_combobox = ttk.Combobox(frm, values=render_device_names, width=max_char, textvariable=pcbValue)
    default_primary_idx = my_render_device.get_index_by_guid(default_primary_device_guid)
    primary_combobox.current(default_primary_idx)
    primary_combobox.bind(
        "<<ComboboxSelected>>",
        lambda _: [
            config_ini.set("RENDER_DEVICE_GUID", "PRIMARY_DEVICE", render_device_guids[primary_combobox.current()]),
            logger.debug(
                "change PRIMARY_DEVICE to \n name: {}\n guid: {}\n".format(
                    render_device_names[primary_combobox.current()],
                    render_device_guids[primary_combobox.current()],
                )
            ),
        ],
    )
    primary_combobox.grid(row=1, column=0)

    secondary_combobox = ttk.Combobox(frm, values=render_device_names, width=max_char, textvariable=scbValue)
    default_secondary_idx = my_render_device.get_index_by_guid(default_secondary_device_guid)
    secondary_combobox.current(default_secondary_idx)
    secondary_combobox.bind(
        "<<ComboboxSelected>>",
        lambda _: [
            config_ini.set(
                "RENDER_DEVICE_GUID", "SECONDARY_DEVICE", render_device_guids[secondary_combobox.current()]
            ),
            logger.debug(
                "change SECONDARY_DEVICE to \n name: {}\n guid: {}\n".format(
                    render_device_names[secondary_combobox.current()],
                    render_device_guids[secondary_combobox.current()],
                )
            ),
        ],
    )
    secondary_combobox.grid(row=1, column=1)

    ttk.Button(frm, text="Save", command=partial(save, config_ini, logger)).grid(row=2, columnspan=2, column=0)

    logger.debug("start main loop.")
    root.mainloop()

    logger.debug("exit config editor.")


if __name__ == "__main__":
    main()
