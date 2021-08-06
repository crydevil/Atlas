from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'resizable', 0)
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
import assistant

class ImageBackground(Widget):
    pass

class InformationButton(Button):
    pass

class RoundedButton(Button):
    pass

class Information(Label):
    pass

class AtlasApp(App):

    def assistant_bt(self, instance):
        assistant.run()

    def message(self, instance):
        layout = FloatLayout()
        layout.add_widget(Information())
        exit_bl = BoxLayout(padding=[225, 860, 225, 20])
        button = Button(text='Закрыть')
        layout.add_widget(exit_bl)
        exit_bl.add_widget(button)
        popup = Popup(title='Информация о приложении', content=layout)
        button.bind(on_press=popup.dismiss)
        popup.open()

    def build(self):
        Window.size = (540, 960)

        canvas = FloatLayout()
        menu_bar = BoxLayout(padding=[0, 0, 0, 860])
        menu_button = BoxLayout(padding=[20, 3, 455, 20])
        assistant_button = BoxLayout(padding=[225, 860, 225, 15])

        canvas.add_widget(ImageBackground())
        canvas.add_widget(menu_bar)
        canvas.add_widget(assistant_button)
        menu_bar.add_widget(menu_button)
        menu_button.add_widget(InformationButton(on_press=app.message))
        assistant_button.add_widget(RoundedButton(on_press=app.assistant_bt))

        return canvas

if __name__ == '__main__':
    app = AtlasApp()
    app.run()