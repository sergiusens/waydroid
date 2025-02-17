# Copyright 2021 Erfan Abdi
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import shutil
import time
import tools.config
import tools.helpers.props
from tools.interfaces import IPlatform
from tools.interfaces import IStatusBarService

def install(args):
    if os.path.exists(tools.config.session_defaults["config_path"]):
        session_cfg = tools.config.load_session()
        if session_cfg["session"]["state"] == "RUNNING":
            tmp_dir = session_cfg["session"]["waydroid_data"] + "/waydroid_tmp"
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)

            shutil.copyfile(args.PACKAGE, tmp_dir + "/base.apk")
            platformService = IPlatform.get_service(args)
            if platformService:
                platformService.installApp("/data/waydroid_tmp/base.apk")
            shutil.rmtree(tmp_dir)
        else:
            logging.error("WayDroid container is {}".format(
                session_cfg["session"]["state"]))
    else:
        logging.error("WayDroid session is stopped")

def remove(args):
    if os.path.exists(tools.config.session_defaults["config_path"]):
        session_cfg = tools.config.load_session()
        if session_cfg["session"]["state"] == "RUNNING":
            platformService = IPlatform.get_service(args)
            if platformService:
                ret = platformService.removeApp(args.PACKAGE)
                if ret != 0:
                    logging.error("Failed to uninstall package: {}".format(args.PACKAGE))
            else:
                logging.error("Failed to access IPlatform service")
        else:
            logging.error("WayDroid container is {}".format(
                session_cfg["session"]["state"]))
    else:
        logging.error("WayDroid session is stopped")

def launch(args):
    def justLaunch():
        platformService = IPlatform.get_service(args)
        if platformService:
            platformService.setprop("waydroid.active_apps", args.PACKAGE)
            ret = platformService.launchApp(args.PACKAGE)
            multiwin = platformService.getprop(
                "persist.waydroid.multi_windows", "false")
            if multiwin == "false":
                platformService.settingsPutString(
                    2, "policy_control", "immersive.status=*")
            else:
                platformService.settingsPutString(
                    2, "policy_control", "immersive.full=*")
        else:
            logging.error("Failed to access IPlatform service")

    if os.path.exists(tools.config.session_defaults["config_path"]):
        session_cfg = tools.config.load_session()

        if session_cfg["session"]["state"] == "RUNNING":
            justLaunch()
        elif session_cfg["session"]["state"] == "FROZEN" or session_cfg["session"]["state"] == "UNFREEZE":
            session_cfg["session"]["state"] = "UNFREEZE"
            tools.config.save_session(session_cfg)
            while session_cfg["session"]["state"] != "RUNNING":
                session_cfg = tools.config.load_session()
            justLaunch()
        else:
            logging.error("WayDroid container is {}".format(
                session_cfg["session"]["state"]))
    else:
        logging.error("WayDroid session is stopped")

def list(args):
    if os.path.exists(tools.config.session_defaults["config_path"]):
        session_cfg = tools.config.load_session()
        if session_cfg["session"]["state"] == "RUNNING":
            platformService = IPlatform.get_service(args)
            if platformService:
                appsList = platformService.getAppsInfo()
                for app in appsList:
                    print("Name: " + app["name"])
                    print("packageName: " + app["packageName"])
                    print("categories:")
                    for cat in app["categories"]:
                        print("\t" + cat)
            else:
                logging.error("Failed to access IPlatform service")
        else:
            logging.error("WayDroid container is {}".format(
                session_cfg["session"]["state"]))
    else:
        logging.error("WayDroid session is stopped")

def showFullUI(args):
    def justShow():
        platformService = IPlatform.get_service(args)
        if platformService:
            platformService.setprop("waydroid.active_apps", "Waydroid")
            platformService.settingsPutString(2, "policy_control", "null*")
            # HACK: Refresh display contents
            statusBarService = IStatusBarService.get_service(args)
            if statusBarService:
                statusBarService.expand()
                time.sleep(0.5)
                statusBarService.collapse()

    if os.path.exists(tools.config.session_defaults["config_path"]):
        session_cfg = tools.config.load_session()

        if session_cfg["session"]["state"] == "RUNNING":
            justShow()
        elif session_cfg["session"]["state"] == "FROZEN" or session_cfg["session"]["state"] == "UNFREEZE":
            session_cfg["session"]["state"] = "UNFREEZE"
            tools.config.save_session(session_cfg)
            while session_cfg["session"]["state"] != "RUNNING":
                session_cfg = tools.config.load_session()
            justShow()
        else:
            logging.error("WayDroid container is {}".format(
                session_cfg["session"]["state"]))
    else:
        logging.error("WayDroid session is stopped")
