from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
#from main import ImageButton
from kivy.app import App
from functools import partial
from specialbuttons import ImageButton, LabelButton
import requests
import kivy.utils
from kivy.graphics import Color, Rectangle


class FriendBanner(FloatLayout):
    def __init__(self, **kwargs):
        #super(FriendBanner, self).__init__(**kwargs)
        super().__init__()
        with self.canvas.before:
            Color(rgba=(kivy.utils.get_color_from_hex("#6C5B7B"))[:3] + [.5])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Make friend id an attribute of this widget so it can be removed later by the app.remove_friend function
        self.friend_id = kwargs['friend_id']

        # Add the friend's avatar
        # Query firebase and order by my_friend_id equalTo friend_id for this person to get their identifer
        check_req = requests.get('https://friendly-fitness.firebaseio.com/.json?orderBy="my_friend_id"&equalTo='
                                 + kwargs['friend_id'])
        data = check_req.json()
        unique_identifer = list(data.keys())[0]
        their_avatar = data[unique_identifer]['avatar']
        print(their_avatar)
        self.remove_label = LabelButton(size_hint=(.10, 1), pos_hint={"top": 1, "right": .1},
                                        on_release=partial(App.get_running_app().remove_friend, kwargs['friend_id']))
        with self.remove_label.canvas.before:
            Color(rgba=(1,0,0,.5))
            self.rect2 = Rectangle(size=self.remove_label.size, pos=self.remove_label.pos)
        self.remove_label.bind(pos=self.update_remove_label_rect, size=self.update_remove_label_rect)

        image_button = ImageButton(source="icons/avatars/" + their_avatar, size_hint=(.3, .8),
                                   pos_hint={"top": .9, "right": 0.5},
                                   on_release=partial(App.get_running_app().load_friend_workout_screen, kwargs['friend_id']))

        # Add the friend's ID
        self.friend_label = LabelButton(text=kwargs['friend_id_text'], markup=True,size_hint=(.5, 1),
                                   pos_hint={"top": 1, "right": 1},
                                   on_release=partial(App.get_running_app().load_friend_workout_screen,
                                                      kwargs['friend_id']))
        self.add_widget(self.remove_label)
        self.add_widget(image_button)
        self.add_widget(self.friend_label)


    def update_friend_label_text(self, new_friend_id_text):
        self.friend_label.text = new_friend_id_text

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


    def update_remove_label_rect(self, *args):
        self.rect2.pos = self.remove_label.pos
        self.rect2.size = self.remove_label.size