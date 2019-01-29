from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
import kivy.utils

class WorkoutBanner(GridLayout):

    def __init__(self, **kwargs):
        self.rows = 1
        super(WorkoutBanner, self).__init__(**kwargs)
        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#67697C")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)


        # Need left FloatLayout
        left = FloatLayout()
        left_image = Image(source="icons/" + kwargs['workout_image'], size_hint=(1, 0.8), pos_hint={"top": 1, "right": 1})
        left_label = Label(text=kwargs['description'], size_hint=(1, .2), pos_hint={"top": .2, "right": 1})
        left.add_widget(left_image)
        left.add_widget(left_label)

        # Need middle FloatLayout
        middle = FloatLayout()
        middle_image = Image(source="icons/" + kwargs['type_image'], size_hint=(1, 0.8), pos_hint={"top": 1, "right": 1})
        middle_label = Label(text=str(kwargs['number']) + " " + kwargs['units'], size_hint=(1, .2), pos_hint={"top": .2, "right": 1})
        middle.add_widget(middle_image)
        middle.add_widget(middle_label)

        # Need right FloatLayout
        right = FloatLayout()
        right_image = Image(source="icons/likes.png", size_hint=(1, 0.8), pos_hint={"top": 1, "right": 1})
        right_label = Label(text=str(kwargs['likes']) + " fist bumps", size_hint=(1, .2), pos_hint={"top": .2, "right": 1})
        right.add_widget(right_image)
        right.add_widget(right_label)

        self.add_widget(left)
        self.add_widget(middle)
        self.add_widget(right)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size







