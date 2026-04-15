from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

from kivymd.uix.widget import MDWidget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogContentContainer,
    MDDialogHeadlineText,
    MDDialogSupportingText,
)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldLeadingIcon


from camera4kivy.preview import Preview
from cv2 import cvtColor, COLOR_RGBA2BGR, COLOR_BGR2GRAY
from numpy import frombuffer,uint8
from pyzbar.pyzbar import decode, ZBarSymbol
from yarl import URL
import jwt
import time
from threading import Thread


class ScannDialog(MDDialog):
    _dialog_headline = None
    _dialog_body = None
    _field_firstname = None
    _field_lastname = None
    _on_continue = None
    _data = None

    def __init__(self, on_continue):
        """Construct the dialog once and cache it."""
        self._dialog_headline = MDDialogHeadlineText(text="Scan Result")

        self._dialog_body = MDDialogSupportingText(text="")

        self._field_firstname = MDTextField(mode="outlined")
        self._field_firstname.add_widget(MDTextFieldLeadingIcon(icon="account"))
        self._field_firstname.add_widget(MDTextFieldHintText(text="First Name"))

        self._field_lastname = MDTextField(mode="outlined")
        self._field_lastname.add_widget(MDTextFieldLeadingIcon(icon="account-outline"))
        self._field_lastname.add_widget(MDTextFieldHintText(text="Last Name"))

        content = MDDialogContentContainer(
            self._field_firstname,
            self._field_lastname,
            orientation="vertical",
            spacing=dp(12),
            padding=(dp(4), 0, dp(4), dp(8)),
            )

        btn_cancel = MDButton(MDButtonText(text="Cancel"),style="text")

        btn_continue = MDButton(MDButtonText(text="Continue"),style="filled")

        buttons = MDDialogButtonContainer(
            MDWidget(),   # spacer → pushes buttons right
            btn_cancel,
            btn_continue,
            spacing=dp(8),
            )

        super().__init__(
            self._dialog_headline,
            self._dialog_body,
            content,
            buttons,
            )

        btn_cancel.bind(on_release=lambda *_: self.dismiss())
        btn_continue.bind(on_release=lambda *_: self.cont())
        
        self._on_continue = on_continue

    def show_scan_dialog(
        self,
        data
        ):
        self._data = data
        
        self._dialog_headline.text = "Valid License" if data["val"] else "Invalid License"
        self._dialog_headline.text_color = get_color_from_hex("#24AF12") if data["val"] else get_color_from_hex("#BD0B0B")
        self._dialog_headline.color = get_color_from_hex("#24AF12") if data["val"] else get_color_from_hex("#BD0B0B")
        self._dialog_headline.theme_text_color = "Custom"
        #self._dialog_body.text = body_text

        self._field_firstname.text = data["FN"]
        self._field_lastname.text = data["LN"]

        self.open()
    
    def cont(self):
        self._data["FN"] = self._field_firstname.text
        self._data["LN"] = self._field_lastname.text
        self.dismiss()
        self._on_continue(self._data)

class ScannerOverlay(MDFloatLayout):
    scan_size = NumericProperty(0)
    bracket_size = NumericProperty(dp(36))
    thickness = NumericProperty(dp(4))
    bracket_color = ListProperty([1, 1, 1, 0.85])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            size=self._redraw,
            pos=self._redraw,
            scan_size=self._redraw,
        )

    def on_size(self, *_):
        # Update scan_size whenever widget is resized
        self.scan_size = min(self.width, self.height) * 0.62

    def _redraw(self, *_):
        self.canvas.before.clear()
        cx, cy = self.center_x, self.center_y
        ss = self.scan_size
        bs = self.bracket_size
        t  = self.thickness

        if ss <= 0:
            return

        lx = cx - ss / 2  # left x of scan window
        rx = cx + ss / 2  # right x
        by = cy - ss / 2  # bottom y
        ty = cy + ss / 2  # top y

        with self.canvas.before:
            # Dark vignette over entire widget
            Color(0, 0, 0, 0.45)
            Rectangle(pos=self.pos, size=self.size)

            # "Cut out" the scan window (transparent)
            Color(0, 0, 0, 0)
            Rectangle(pos=(lx, by), size=(ss, ss))

            # Corner brackets
            Color(*self.bracket_color)

            # Top-left
            Line(points=[lx, ty - bs, lx, ty, lx + bs, ty],
                 width=t, cap="none")
            # Top-right
            Line(points=[rx - bs, ty, rx, ty, rx, ty - bs],
                 width=t, cap="none")
            # Bottom-left
            Line(points=[lx, by + bs, lx, by, lx + bs, by],
                 width=t, cap="none")
            # Bottom-right
            Line(points=[rx - bs, by, rx, by, rx, by + bs],
                 width=t, cap="none")


class CPreview(Preview):
    _analyzing = False  # prevent overlapping threads
    on_detect = None
    analyze = True
    _last_analyze = 0
    _analyze_interval = 0.2

    def __init__(self, **kwargs):
        super().__init__(aspect_ratio = '16:9', **kwargs)

    def bind_on_recv(self, on_detect):
        self.on_detect = on_detect

    def analyze_pixels_callback(self, pixels, image_size, image_pos, image_scale, mirror):
        if not self.analyze or self._analyzing:
            return
        
        now = time.time()
        if now - self._last_analyze < self._analyze_interval:
            return
        self._last_analyze = now
        
        # copy pixels before handing off — buffer may be reused
        pixels_copy = bytes(pixels)
        self._analyzing = True
        Thread(
            target=self._analyze,
            args=(pixels_copy, image_size),
            daemon=True
        ).start()

    def _analyze(self, pixels, image_size):
        try:
            w, h = image_size
            frame = frombuffer(pixels, dtype=uint8).reshape(h, w, 4)
            frame = cvtColor(frame, COLOR_RGBA2BGR)
            gray = cvtColor(frame, COLOR_BGR2GRAY)

            for qr in decode(gray, symbols=[ZBarSymbol.QRCODE]):
                data = qr.data.decode()
                if data.startswith("https://qr"):
                    token = URL(data).query.get("s")
                    data = jwt.decode(token, options={"verify_signature": False})
                    if data.get("LTN") == "Judopass" and self.on_detect:
                        Clock.schedule_once(lambda dt, d=data: self.on_detect(d))
        finally:
            self._analyzing = False


# base qrcode scanner screen class
class ScannerScreen(MDScreen):
    camera: CPreview
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera = CPreview(size_hint= (1, 1))
        Clock.schedule_once(self.builds)
    
    def builds(self, *args):
        self.add_widget(
            MDFloatLayout(
                self.camera,
                ScannerOverlay(
                    size_hint= (1, 1),
                    pos= (0, 0)
                )
            )
        )