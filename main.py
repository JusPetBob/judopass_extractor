from kivy.utils import platform
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemIcon, MDNavigationItemLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screenmanager import MDScreenManager
from kivy.storage.jsonstore import JsonStore

import time

from scanner_page import *

import os


class BaseMDNavigationItem(MDNavigationItem):
    def __init__(self, icon, text, *args, **kwargs):
        self.icon = icon
        self.text = text
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
    store:JsonStore
    path:str
    df:dict
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if platform == "android":
            self.path = os.path.join(path, "data.json")
        else:
            self.path = os.path.join(path, "test_app", "data.json")
        
        self.store = JsonStore(self.path)
        
        cols = ['FN', 'LN', 'val', 'exp', 'iss', 'UID', 'NO', 'CID', 'ID', 'DOB', 'NAT', 'TM', 'LT', 'LTN', 'LT2', 'KEY']
        
        if self.store.exists("df"):
            self.df = self.store.get("df")
            if set(self.df.keys()) != set(cols):
                self.df = {i:[] for i in cols}
        else:
            self.df = {i:[] for i in cols}

    
    def set_data(self,data):
        print(self.df,data)
        self.df = dict(map(lambda kv, data=data: self.append(kv,data),self.df.items()))
        #self.df = pd.concat([pd.DataFrame(data, columns=self.df.columns, index=[0]), self.df], ignore_index=True)
        #self.store.put('df', data=self.df.to_dict())
        print(self.df)
    
    def append(self,kv,data):
        k,v=kv
        
        if v is None:
            v = []
        
        v.insert(0,data[k])
        
        return k,v
        
    
    def print_data(self):
        import json
        print(json.dumps(self.df,indent=4))


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
        t = time.time()
        
        print(item_text)
        
        if item_text == "List":
            self.list_screen.print_data()
        
        self.screen_manager.current = item_text
        
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
        self.scanner_screen = ScannerScreen(name="Scanner")
        self.camera = self.scanner_screen.camera
        
        self.list_screen = ListScreen(self.user_data_dir,name="List")
        
        self.screen_manager = MDScreenManager(
            self.scanner_screen,
            self.list_screen
        )
        
        return MDBoxLayout(
            self.screen_manager,
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
        self.camera.bind_on_recv(self.recive_qr_raw)
        self.camera.connect_camera(enable_analyze_pixels=True)
    
    def recive_qr_raw(self,payload:dict):
        payload["val"] = payload["exp"] > time.time()
        
        print(self.dialog.is_open)
        
        if not self.dialog.is_open:
        
            self.dialog = ScannDialog(self.accepted,lambda: self.set_camera(True))
            self.dialog.show_scan_dialog(payload)
        
            self.set_camera(False)
    
    def set_camera(self,t:bool):
        self.camera.analyze = t
        
    def accepted(self,payload:dict):
        if self.dialog:
            self.set_camera(True)
        
        self.list_screen.set_data(payload)
        
        
        

if __name__ == "__main__":
    if platform == "android":
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.CAMERA])
    App().run()