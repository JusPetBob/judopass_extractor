from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import platform
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.screen import MDScreen

from camera4kivy.preview import Preview
from cv2 import QRCodeDetector,cvtColor, COLOR_RGBA2BGR, COLOR_BGR2GRAY
from numpy import frombuffer,uint8
from pyzbar.pyzbar import decode
from yarl import URL
import jwt

# base navigation class 
class BaseMDNavigationItem(MDNavigationItem):
    badge = ObjectProperty(None)
    icon = StringProperty()
    text = StringProperty()

    def set_badge(self, value):
        if self.badge:
            self.badge.text = str(value)

# base qrcode scanner screen class
class ScannerScreen(MDScreen):
    image_size = StringProperty()


class CPreview(Preview):
    detector = QRCodeDetector()
    
    def __init__(self, **kwargs):
        super().__init__(aspect_ratio = '16:9', **kwargs)
    
    def analyze_pixels_callback(self, pixels, image_size, image_pos, image_scale, mirror):
        w, h = image_size
        
        frame = frombuffer(pixels, dtype=uint8).reshape(h, w, 4)
        
        frame = cvtColor(frame, COLOR_RGBA2BGR)
        
        gray = cvtColor(frame, COLOR_BGR2GRAY)
        
        for qr in decode(gray):
            data = qr.data.decode()
            if data.startswith("https://"):
                token = URL(data).query("s")
                print(jwt.decode(token, options={"verify_signature":False}))

# base list screen class
class ListScreen(MDScreen):
    image_size = StringProperty()


#standard app
class App(MDApp):
    def on_switch_tabs(
            self,
            bar: MDNavigationBar,
            item: MDNavigationItem,
            item_icon: str,
            item_text: str,
        ):
        self.root.ids.screen_manager.current = item_text
        
        #self.root.ids.list_item.set_badge(5)

    def build(self):
        return Builder.load_file("app.kv")
    
    def on_start(self):
        screen = self.root.ids.screen_manager.get_screen("Scanner")
        self.camera = screen.ids.camera
        self.camera.connect_camera(enable_analyze_pixels=True)


if __name__ == "__main__":
    if platform == "android":
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.CAMERA])
    App().run()