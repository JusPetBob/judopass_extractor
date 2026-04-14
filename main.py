from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import platform
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.screen import MDScreen

import time

from scanner_page import *


# base navigation class 
class BaseMDNavigationItem(MDNavigationItem):
    badge = ObjectProperty(None)
    icon = StringProperty()
    text = StringProperty()

    def set_badge(self, value):
        if self.badge:
            self.badge.text = str(value)

# base list screen class
class ListScreen(MDScreen):
    image_size = StringProperty()


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
        self.root.ids.screen_manager.current = item_text
        
        if item_text == "Scanner":
            self.camera.connect_camera(enable_analyze_pixels=True)
        else:
            self.camera.disconnect_camera()
        
        #self.root.ids.list_item.set_badge(5)
    
    def on_pause(self):
        if self.camera:
            self.camera.disconnect_camera()
    
    def on_resume(self):
        if self.camera:
            self.camera.disconnect_camera()

    def build(self):
        return Builder.load_file("app.kv")
    
    def on_start(self):
        self.dialog = ScannDialog(self.accepted)
        screen = self.root.ids.screen_manager.get_screen("Scanner")
        self.camera = screen.ids.camera
        self.camera.bind_on_recv(self.recive_qr_raw)
        self.camera.connect_camera(enable_analyze_pixels=True)
    
    def recive_qr_raw(self,payload:dict):
        payload["val"] = payload["exp"] > time.time()
        if self.dialog:
            self.camera.analyze = False
            Clock.schedule_once(lambda dt: self.dialog.show_scan_dialog(payload))
            
    def accepted(self,payload:dict):
        if self.dialog:
            self.camera.analyze = True
        print(payload, flush=True)
        

if __name__ == "__main__":
    if platform == "android":
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.CAMERA])
    App().run()