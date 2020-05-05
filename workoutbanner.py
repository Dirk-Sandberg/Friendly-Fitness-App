from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.app import App
import kivy.utils

class WorkoutBanner(GridLayout):

    def on_touch_down(self, touch):
        # Make it so if there's a double tap and it's a friend workout banner (not your own!) it registers a like
        if self.likeable:
            if touch.is_double_tap:
                if self.collide_point(*touch.pos):
                    app = App.get_running_app()
                    # Someone double tapped the banner.
                    # Add one to the like label in the banner
                    likes = self.right_label.text.split(" ")[0]
                    likes = str(int(likes) + 1)
                    self.right_label.text = likes + " " + " ".join(self.right_label.text.split(" ")[1:])

                    # Need to update firebase for this user
                    # Need to know their friend id
                    their_friend_id = App.get_running_app().their_friend_id  # Set each time someone clicks on their friends banner
                    # Need to have rules allow write to /likes
                    # Need to write to /likes
                    app.my_firebase.update_likes(their_friend_id, self.workout_key, likes)


    def __init__(self, **kwargs):
        self.rows = 1
        try:
            # Pass kwarg likeable=True to a WorkoutBanner to enable double-tap-to-like
            self.likeable = kwargs['likeable']
            self.workout_key = kwargs['workout_key']
        except:
            self.likeable = False
            self.workout_key = ""

        #super(WorkoutBanner, self).__init__(**kwargs)
        super().__init__()#**kwargs)
        with self.canvas.before:
            Color(rgba=(kivy.utils.get_color_from_hex("#6C5B7B"))[:3] + [.5])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)


        # Need left FloatLayout
        left = FloatLayout()
        left_image = Image(source="icons/workouts/" + kwargs['workout_image'], size_hint=(1, 0.5), pos_hint={"top": .75, "right": 1})
        left_label = Label(text=kwargs['description'], size_hint=(1, .2), pos_hint={"top": .225, "right": 1})
        left.add_widget(left_image)
        left.add_widget(left_label)

        # Need middle FloatLayout
        middle = FloatLayout()
        middle_date = Label(text=kwargs['date'], size_hint=(1, .2), pos_hint={"top": .975, "right": 1})
        middle_image = Image(source=kwargs['type_image'], size_hint=(1, 0.5), pos_hint={"top": .75, "right": 1})
        middle_label = Label(text=str(kwargs['number']) + " " + kwargs['units'], size_hint=(1, .2), pos_hint={"top": .225, "right": 1})
        middle.add_widget(middle_date)
        middle.add_widget(middle_image)
        middle.add_widget(middle_label)

        # Need right FloatLayout
        right = FloatLayout()
        right_image = Image(source="icons/likes.png", size_hint=(1, 0.5), pos_hint={"top": .75, "right": 1})
        self.right_label = Label(text=str(kwargs['likes']) + " fist bumps", size_hint=(1, .2), pos_hint={"top": .225, "right": 1})
        right.add_widget(right_image)
        right.add_widget(self.right_label)

        self.add_widget(left)
        self.add_widget(middle)
        self.add_widget(right)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size







