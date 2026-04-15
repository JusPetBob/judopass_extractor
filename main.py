from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import platform
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemIcon, MDNavigationItemLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screenmanager import MDScreenManager

import time

from scanner_page import *

from threading import Thread


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(self.builds)

    def builds(self, *args):
        self.add_widget(
            MDNavigationItemIcon(
                icon=self.icon
            )
        )
        self.add_widget(
            MDNavigationItemLabel(
                text=self.text
            )
        )

# base list screen class
class ListScreen(MDScreen):
    pass


#standard app
class App(MDApp):
    dialog:ScannDialog = None
    camera = None
    
    def on_switch_tabs(
            self,
            bar: MDNavigationBar,
            item: MDNavigationItem,
            item_icon: str,
            item_text: str,
        ):
        t= time.time()
        
        self.root.get_ids().screen_manager.current = item_text
        
        if item_text == "Scanner":
            self.camera.analyze = True
            #Clock.schedule_once(lambda dt: self.camera.connect_camera(enable_analyze_pixels=True))
        else:
            self.camera.analyze = False
            #Clock.schedule_once(lambda dt: self.camera.disconnect_camera())
        
        #self.root.ids.list_item.set_badge(5)
    
    def on_pause(self):
        if self.camera:
            self.camera.disconnect_camera()
    
    def on_resume(self):
        if self.camera:
            self.camera.connect_camera(enable_analyze_pixels=True)

    def build(self):
        return MDBoxLayout(
            MDScreenManager(
                ScannerScreen(name="Scanner"),
                ListScreen(name="List"),
                id="screen_manager"
                ),
            MDNavigationBar(
                BaseMDNavigationItem(
                    icon="camera",
                    text="Scanner",
                    active=True,
                    ),
                BaseMDNavigationItem(
                    icon="format-list-bulleted",
                    text="List",
                    ),
                on_switch_tabs=lambda *args: self.on_switch_tabs(*args)
                ),
            orientation= "vertical",
            md_bg_color= self.theme_cls.backgroundColor
            )
            
    
    def on_start(self):
        self.dialog = ScannDialog(self.accepted)
        screen = self.root.get_ids().screen_manager.get_screen("Scanner")
        self.camera = screen.camera
        self.camera.bind_on_recv(self.recive_qr_raw)
        Thread(target=lambda: self.camera.connect_camera(enable_analyze_pixels=True),daemon=True).start()
    
    def recive_qr_raw(self,payload:dict):
        payload["val"] = payload["exp"] > time.time()
        if self.dialog:
            self.camera.analyze = False
            self.dialog.show_scan_dialog(payload)
            
    def accepted(self,payload:dict):
        if self.dialog:
            self.camera.analyze = True
        print(payload, flush=True)
        

if __name__ == "__main__":
    if platform == "android":
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.CAMERA])
    App().run()