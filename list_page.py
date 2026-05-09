# base list screen class
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.divider import MDDivider

from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
from kivy.metrics import dp

import os

class TableRow(MDCard):
    style = "outlined"
    def __init__(self, cols: list, data, **kwargs):
        super().__init__(**kwargs)

        self.size_hint_y = None
        self.height = dp(48)

        layout = MDBoxLayout()
        layout.bind(minimum_width=layout.setter("width"))
        self.cols = cols
        
        for i in self.cols:
            l = MDLabel(
                text=str(data.get(i, "")),
                size_hint_x=None,
                width=dp(120),
                shorten=True,
                padding=[10,0]
                )
            layout.add_widget(l)
            
            layout.add_widget(MDDivider(orientation="vertical"))

        self.add_widget(layout)

class ListScreen(MDScreen):
    store:JsonStore
    path:str
    df:list
    cols = ['FN', 'LN', 'val', 'exp', 'iss', 'UID', 'NO', 'CID', 'ID', 'DOB', 'NAT', 'TM', 'LT', 'LTN', 'LT2', 'KEY']
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if platform == "android":
            self.path = os.path.join(path, "data.json")
        else:
            self.path = os.path.join(path, "test_app", "data.json")
        
        self.store = JsonStore(self.path)
        
        if self.store.exists("df"):
            self.df = self.store.get("df").get("values")
            print(self.df)
            if not isinstance(self.df,list) or set(self.df[0].keys()) != set(self.cols):
                self.df = []
        else:
            self.df = []
        
        self.rv = MDScrollView(do_scroll_x=True,do_scroll_y=True)

        self.layout = MDBoxLayout(
            orientation="vertical",
            size_hint=(1,None)
        )
        self.layout.bind(minimum_height=self.layout.setter("height"))
        
        self.rv.add_widget(self.layout)
    
        self.add_widget(self.rv)
        
        
        for i in [{c:c for c in self.cols}]+self.df:
            self.layout.add_widget(TableRow(self.cols, i))
    
    def set_data(self,data):
        print(self.df,data)
        
        self.df.insert(0,data)
        
        print(self.df)

        self.store.put(key='df', values=self.df)
    
    def print_data(self):
        import json
        print(json.dumps(self.df,indent=4))