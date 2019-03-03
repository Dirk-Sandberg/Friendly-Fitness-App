import sys
sys.path.append("/".join(x for x in __file__.split("/")[:-1]))
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from specialbuttons import ImageButton, LabelButton, ImageButtonSelectable
from workoutbanner import WorkoutBanner
from functools import partial
from os import walk
from myfirebase import MyFirebase
from datetime import datetime
from friendbanner import FriendBanner
import kivy.utils
import requests
import json
import traceback
from kivy.graphics import Color, RoundedRectangle
import helperfunctions


class HomeScreen(Screen):
    pass

class AddFriendScreen(Screen):
    pass

class AddWorkoutScreen(Screen):
    pass

class FriendWorkoutScreen(Screen):
    pass

class FriendsListScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class ChangeAvatarScreen(Screen):
    pass

GUI = Builder.load_file("main.kv")  # Make sure this is after all class definitions!
class MainApp(App):
    my_friend_id = ""
    workout_image = None
    option_choice = None
    workout_image_widget = ""
    previous_workout_image_widget = None
    friends_list = ""
    refresh_token_file = "refresh_token.txt"


    def build(self):
        self.my_firebase = MyFirebase()
        return GUI

    def update_workout_image(self, filename, widget_id):
        self.previous_workout_image_widget = self.workout_image_widget
        self.workout_image = filename
        self.workout_image_widget = widget_id
        # Clear the indication that the previous image was selected
        if self.previous_workout_image_widget:
            self.previous_workout_image_widget.canvas.before.clear()
        # Make sure the text color of the label above the scrollview is white (incase it was red from them earlier)
        select_workout_image_label = self.root.ids.add_workout_screen.ids.select_workout_image_label
        select_workout_image_label.color = (1, 1, 1, 1)

        # Indicate which image has been selected
        with self.workout_image_widget.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#6C5B7B")))
            RoundedRectangle(size=self.workout_image_widget.size, pos=self.workout_image_widget.pos, radius = [5,])


    def on_start(self):
        # Choose the correct time icon to show based on the current hour of day
        now = datetime.now()
        hour = now.hour
        if hour <= 6:
            self.root.ids['time_indicator1'].opacity = 1
        elif hour <= 12:
            self.root.ids['time_indicator2'].opacity = 1
        elif hour <= 18:
            self.root.ids['time_indicator3'].opacity = 1
        else:
            self.root.ids['time_indicator4'].opacity = 1

        # Set the current day, month, and year in the add workout section
        day, month, year = now.day, now.month, now.year
        self.root.ids.add_workout_screen.ids.month_input.text = str(month)
        self.root.ids.add_workout_screen.ids.day_input.text = str(day)
        self.root.ids.add_workout_screen.ids.year_input.text = str(year)

        # Populate avatar grid
        avatar_grid = self.root.ids['change_avatar_screen'].ids['avatar_grid']
        for root_dir, folders, files in walk("icons/avatars"):
            for f in files:
                img = ImageButtonSelectable(source="icons/avatars/" + f, on_release=partial(self.change_avatar, f))
                avatar_grid.add_widget(img)

        # Populate workout image grid
        workout_image_grid = self.root.ids['add_workout_screen'].ids['workout_image_grid']
        for root_dir, folders, files in walk("icons/workouts"):
            for f in files:
                if '.png' in f:
                    img = ImageButton(source="icons/workouts/" + f, on_release=partial(self.update_workout_image, f))
                    workout_image_grid.add_widget(img)


        try:
            # Try to read the persistent signin credentials (refresh token)
            with open(self.refresh_token_file, 'r') as f:
                refresh_token = f.read()
            # Use refresh token to get a new idToken
            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # Get database data
            result = requests.get("https://friendly-fitness.firebaseio.com/" + local_id + ".json?auth=" + id_token)
            data = json.loads(result.content.decode())
            self.my_friend_id = data['my_friend_id']
            friend_id_label = self.root.ids['settings_screen'].ids['friend_id_label']
            friend_id_label.text = "Friend ID: " + str(self.my_friend_id)

            # Get and update avatar image
            avatar_image = self.root.ids['avatar_image']
            avatar_image.source = "icons/avatars/" + data['avatar']

            # Get friends list
            self.friends_list = data['friends']

            # Populate friends list grid
            friends_list_array = self.friends_list.split(",")
            for friend in friends_list_array:
                friend = friend.replace(" ", "")
                if friend == "":
                    continue
                friend_banner = FriendBanner(friend_id = friend)
                self.root.ids['friends_list_screen'].ids['friends_list_grid'].add_widget(friend_banner)


            # Get and update streak label
            streak_label = self.root.ids['home_screen'].ids['streak_label']
            #streak_label.text = str(data['streak']) + " Day Streak" # Thisis updated if there are workouts


            # Set the images in the add_workout_screen
            banner_grid = self.root.ids['home_screen'].ids['banner_grid']
            workouts = data['workouts']
            if workouts != "":
                workout_keys = workouts.keys()
                streak = helperfunctions.count_workout_streak(workouts)
                streak_label.text = str(streak) + " Day Streak"
                # Sort workouts by date then reverse (we want youngest dates at the start)
                workout_keys.sort(key = lambda value : datetime.strptime(workouts[value.encode()]['date'].encode('utf-8'), "%m/%d/%Y"))
                workout_keys = workout_keys[::-1]
                for workout_key in workout_keys:
                    workout = workouts[workout_key]
                    # Populate workout grid in home screen
                    W = WorkoutBanner(workout_image=workout['workout_image'], description=workout['description'],
                                      type_image=workout['type_image'], number=workout['number'], units=workout['units'],
                                      likes=workout['likes'], date=workout['date'])
                    banner_grid.add_widget(W)

            self.change_screen("home_screen", "None")

        except Exception as e:
            traceback.print_exc()
            pass

    def set_friend_id(self, my_friend_id):
        self.my_friend_id = my_friend_id
        friend_id_label = self.root.ids['settings_screen'].ids['friend_id_label']
        friend_id_label.text = "Friend ID: " + str(self.my_friend_id)


    def add_friend(self, friend_id):
        friend_id = friend_id.replace("\n","")
        # Make sure friend id was a number otherwise it's invalid
        try:
            int_friend_id = int(friend_id)
        except:
            # Friend id had some letters in it when it should just be a number
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "Friend ID should be a number."
            return
        # Make sure they aren't adding themselves
        if friend_id == self.my_friend_id:
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "You can't add yourself as a friend."
            return

        # Make sure this is not someone already in their friends list
        if friend_id in self.friends_list.split(","):
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "This user is already in your friend's list."
            return


        # Query database and make sure friend_id exists
        check_req = requests.get('https://friendly-fitness.firebaseio.com/.json?orderBy="my_friend_id"&equalTo=' + friend_id)
        data = check_req.json()

        if data == {}:
            # If it doesn't, display it doesn't in the message on the add friend screen
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "Invalid friend ID"
        else:
            # Requested friend ID exists
            key = data.keys()[0]
            #new_friend_id = data[key]['my_friend_id']

            # Add friend id to friends list and patch new friends list
            self.friends_list += ",%s"  % friend_id
            patch_data = '{"friends": "%s"}' %self.friends_list
            patch_req = requests.patch("https://friendly-fitness.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token),
                                       data=patch_data)

            # Add new friend banner in friends list screen
            friend_banner = FriendBanner(friend_id=friend_id)
            self.root.ids['friends_list_screen'].ids['friends_list_grid'].add_widget(friend_banner)
            # Inform them they added a friend successfully
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "Friend ID %s added successfully."%friend_id

    def sign_out_user(self):
        # User wants to log out
        with open(self.refresh_token_file, 'w') as f:
            f.write("")
        self.change_screen("login_screen", direction='down', mode='push')
        # Need to set the avatar to the default image
        avatar_image = self.root.ids['avatar_image']
        avatar_image.source = "icons/avatars/man.png"



        # Need to clear widgets from previous user's friends list
        friends_list_grid = self.root.ids['friends_list_screen'].ids['friends_list_grid']
        for w in friends_list_grid.walk():
            if w.__class__ == FriendBanner:
                friends_list_grid.remove_widget(w)

        # Need to clear widgets from previous user's workout grid
        workout_banner = self.root.ids['home_screen'].ids['banner_grid']
        for w in workout_banner.walk():
            if w.__class__ == WorkoutBanner:
                workout_banner.remove_widget(w)

        # Need to clear widgets from previous user's friend's workout grid
        friend_banner_grid = self.root.ids['friend_workout_screen'].ids['friend_banner_grid']
        for w in friend_banner_grid.walk():
            if w.__class__ == WorkoutBanner:
                friend_banner_grid.remove_widget(w)


    def change_avatar(self, image, widget_id):
        # Change avatar in the app
        avatar_image = self.root.ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image


        # Change avatar in firebase database
        my_data = '{"avatar": "%s"}' % image
        requests.patch(
            "https://friendly-fitness.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token),
            data=my_data)

        self.change_screen("settings_screen", direction='left', mode='pop')

    def add_workout(self):
        # Get data from all fields in add workout screen
        workout_ids = self.root.ids['add_workout_screen'].ids

        workout_image_grid = self.root.ids['add_workout_screen'].ids['workout_image_grid']
        select_workout_image_label = self.root.ids.add_workout_screen.ids.select_workout_image_label

        # Already have workout image in self.workout_image variable
        description_input = workout_ids['description_input'].text.replace("\n","")
        # Already have option choice in self.option_choice
        quantity_input = workout_ids['quantity_input'].text.replace("\n","")
        units_input = workout_ids['units_input'].text.replace("\n","")
        month_input = workout_ids['month_input'].text.replace("\n","")
        day_input = workout_ids['day_input'].text.replace("\n","")
        year_input = workout_ids['year_input'].text.replace("\n","")

        # Make sure fields aren't garbage
        if self.workout_image == None:
            select_workout_image_label.color = (1,0,0,1)
            return
        # They are allowed to leave no description
        if self.option_choice == None:
            workout_ids['time_label'].color = (1,0,0,1)
            workout_ids['distance_label'].color = (1,0,0,1)
            workout_ids['sets_label'].color = (1,0,0,1)
            return
        try:
            int_quantity = float(quantity_input)
        except:
            workout_ids['quantity_input'].background_color = (1,0,0,1)
            return
        if units_input == "":
            workout_ids['units_input'].background_color = (1,0,0,1)
            return
        try:
            int_month = int(month_input)
            if int_month > 12:
                workout_ids['month_input'].background_color = (1, 0, 0, 1)
                return
        except:
            workout_ids['month_input'].background_color = (1,0,0,1)
            return
        try:
            int_day = int(day_input)
            if int_day > 31:
                workout_ids['day_input'].background_color = (1, 0, 0, 1)
                return
        except:
            workout_ids['day_input'].background_color = (1,0,0,1)
            return
        try:
            if len(year_input) == 2:
                year_input = '20'+year_input
            int_year = int(year_input)
        except:
            workout_ids['year_input'].background_color = (1,0,0,1)
            return

        # If all data is ok, send the data to firebase real-time database
        workout_payload = {"workout_image": self.workout_image, "description": description_input, "likes": 0,
                           "number": float(quantity_input), "type_image": self.option_choice, "units": units_input,
                           "date": month_input + "/" + day_input + "/" + year_input}
        workout_request = requests.post("https://friendly-fitness.firebaseio.com/%s/workouts.json?auth=%s"
                                        %(self.local_id, self.id_token), data=json.dumps(workout_payload))
        # Add the workout to the banner grid in the home screen
        banner_grid = self.root.ids['home_screen'].ids['banner_grid']
        W = WorkoutBanner(workout_image=self.workout_image, description=description_input,
                          type_image=self.option_choice, number=float(quantity_input), units=units_input,
                          likes="0", date=month_input + "/" + day_input + "/" + year_input)
        banner_grid.add_widget(W, index=len(banner_grid.children))

        # Check if the new workout has made their streak increase
        streak_label = self.root.ids['home_screen'].ids['streak_label']
        result = requests.get("https://friendly-fitness.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
        data = json.loads(result.content.decode())
        workouts = data['workouts']
        streak = helperfunctions.count_workout_streak(workouts)
        streak_label.text = str(streak) + " Day Streak"

        # Go back to the home screen
        self.change_screen("home_screen", direction="backwards")


    def remove_friend(self, friend_id_to_remove, *args):
        # Remove the friend id from the friends list variable
        self.friends_list = self.friends_list.replace(",%s"%friend_id_to_remove, "")

        # Update the firebase database with the new (truncated) friends list
        patch_data = '{"friends": "%s"}' % self.friends_list
        patch_req = requests.patch(
            "https://friendly-fitness.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token),
            data=patch_data)

        # Remove the friend banner
        friends_list_grid = self.root.ids['friends_list_screen'].ids['friends_list_grid']
        for w in friends_list_grid.walk():
            if w.__class__ == FriendBanner:
                if w.friend_id == friend_id_to_remove:
                    friends_list_grid.remove_widget(w)

        # Reload the friends list screen

    def load_friend_workout_screen(self, friend_id, widget):
        # Get their workouts by using their friend id to query the database
        friend_data_req = requests.get('https://friendly-fitness.firebaseio.com/.json?orderBy="my_friend_id"&equalTo=' + friend_id)

        friend_data = friend_data_req.json()
        workouts = friend_data.values()[0]['workouts']

        friend_banner_grid = self.root.ids['friend_workout_screen'].ids['friend_banner_grid']

        # Remove each widget in the friend_banner_grid
        for w in friend_banner_grid.walk():
            if w.__class__ == WorkoutBanner:
                friend_banner_grid.remove_widget(w)

        # Populate their avatar image
        friend_avatar_image = self.root.ids.friend_workout_screen.ids.friend_workout_screen_image
        friend_avatar_image.source = "icons/avatars/" + friend_data.values()[0]['avatar']

        # Populate their friend ID and nickname
        print("Need to populate nickname")
        their_friend_id_label = self.root.ids.friend_workout_screen.ids.friend_workout_screen_friend_id
        their_friend_id_label.text = "Friend ID: " + friend_id

        # Populate the friend_workout_screen
        # Loop through each key in the workouts dictionary
        #    for the value for that key, create a workout banner
        #    add the workout banner to the scrollview
        if workouts == {} or workouts == "":
            # Change to the friend_workout_screen
            self.change_screen("friend_workout_screen")
            return
        workout_keys = workouts.keys()
        workout_keys.sort(key=lambda value: datetime.strptime(workouts[value.encode()]['date'].encode('utf-8'), "%m/%d/%Y"))
        workout_keys = workout_keys[::-1]
        for workout_key in workout_keys:
            workout = workouts[workout_key]
            W = WorkoutBanner(workout_image=workout['workout_image'], description=workout['description'],
                              type_image=workout['type_image'], number=workout['number'], units=workout['units'],
                              likes=workout['likes'],date=workout['date'])
            friend_banner_grid.add_widget(W)

        # Populate the streak label
        friend_streak_label = self.root.ids['friend_workout_screen'].ids['friend_streak_label']
        friend_streak_label.text = helperfunctions.count_workout_streak(workouts) + " Day Streak"


        # Change to the friend_workout_screen
        self.change_screen("friend_workout_screen")

    def change_screen(self, screen_name, direction='forward', mode = ""):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']
        #print(direction, mode)
        # If going backward, change the transition. Else make it the default
        # Forward/backward between pages made more sense to me than left/right
        if direction == 'forward':
            mode = "push"
            direction = 'left'
        elif direction == 'backwards':
            direction = 'right'
            mode = 'pop'
        elif direction == "None":
            screen_manager.transition = NoTransition()
            screen_manager.current = screen_name
            return

        screen_manager.transition = CardTransition(direction=direction, mode=mode)

        screen_manager.current = screen_name

MainApp().run()
