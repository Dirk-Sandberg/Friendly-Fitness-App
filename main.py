from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from workoutbanner import WorkoutBanner
from kivy.uix.label import Label
from functools import partial
from os import walk
from myfirebase import MyFirebase
import requests
import json


class HomeScreen(Screen):
    pass

class AddFriendScreen(Screen):
    pass

class LabelButton(ButtonBehavior, Label):
    pass

class ImageButton(ButtonBehavior, Image):
    pass

class LoginScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class ChangeAvatarScreen(Screen):
    pass

GUI = Builder.load_file("main.kv")  # Make sure this is after all class definitions!
class MainApp(App):
    my_friend_id = 1
    def build(self):
        self.my_firebase = MyFirebase()
        return GUI

    def on_start(self):
        # Populate avatar grid
        avatar_grid = self.root.ids['change_avatar_screen'].ids['avatar_grid']
        for root_dir, folders, files in walk("icons/avatars"):
            for f in files:
                img = ImageButton(source="icons/avatars/" + f, on_release=partial(self.change_avatar, f))
                avatar_grid.add_widget(img)


        try:
            # Try to read the persisten signin credentials (refresh token)
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()
            # Use refresh token to get a new idToken
            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # Get database data
            result = requests.get("https://friendly-fitness.firebaseio.com/" + local_id + ".json?auth=" + id_token)
            print("res ok?", result.ok)
            print(result.json())
            data = json.loads(result.content.decode())

            # Get and update avatar image
            avatar_image = self.root.ids['avatar_image']
            avatar_image.source = "icons/avatars/" + data['avatar']

            # Get friends list
            self.friends_list = data['friends']

            # Get and update streak label
            streak_label = self.root.ids['home_screen'].ids['streak_label']
            streak_label.text = str(data['streak']) + " Day Streak!"

            # Get and update friend id label
            friend_id_label = self.root.ids['settings_screen'].ids['friend_id_label']
            friend_id_label.text = "Friend ID: " + str(self.my_friend_id)

            banner_grid = self.root.ids['home_screen'].ids['banner_grid']
            workouts = data['workouts'][1:]
            for workout in workouts:
                for i in range(5):
                    # Populate workout grid in home screen
                    W = WorkoutBanner(workout_image=workout['workout_image'], description=workout['description'],
                                      type_image=workout['type_image'], number=workout['number'], units=workout['units'],
                                      likes=workout['likes'])
                    banner_grid.add_widget(W)

            self.root.ids['screen_manager'].transition = NoTransition()
            self.change_screen("home_screen")
            self.root.ids['screen_manager'].transition = CardTransition()

        except Exception as e:
            print(e)
            pass

    def add_friend(self, friend_id):
        # Query database and make sure friend_id exists
        check_req = requests.get('https://friendly-fitness.firebaseio.com/.json?orderBy="my_friend_id"&equalTo=' + friend_id)
        data = check_req.json()

        if data == {}:
            # If it doesn't, display it doesn't in the message on the add friend screen
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "Invalid friend ID"
        else:
            key = data.keys()[0]
            new_friend_id = data[key]['my_friend_id']
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "Friend ID %s added successfully."%friend_id
            # Add friend id to friends list and patch new friends list
            self.friends_list += ", %s"  % friend_id
            patch_data = '{"friends": "%s"}' %self.friends_list
            patch_req = requests.patch("https://friendly-fitness.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token),
                                       data=patch_data)
            print(patch_req.ok)
            print(patch_req.json())


        # If it does, display "success"
        # If it does, add to friends list

    def change_avatar(self, image, widget_id):
        # Change avatar in the app
        avatar_image = self.root.ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image


        # Change avatar in firebase database
        my_data = '{"avatar": "%s"}' % image
        requests.patch("https://friendly-fitness.firebaseio.com/" + str(self.my_friend_id) + ".json",
                       data=my_data)

        self.change_screen("settings_screen")


    def change_screen(self, screen_name):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name

MainApp().run()
