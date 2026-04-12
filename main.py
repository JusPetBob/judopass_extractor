from kivymd.app import MDApp
from kivy.lang import Builder

class MainApp():
    pass

class App(MDApp):
    def build(self):
        return Builder.load_file("app.kv")


if __name__ == "__main__":
    App().run()