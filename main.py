from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.screen import MDScreen

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


if __name__ == "__main__":
    if platform == "android":
        from android.permissions import request_permissions, Permissions
        request_permissions([Permissions.CAMERA])
    App().run()