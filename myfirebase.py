import requests
import json
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
import certifi

class MyFirebase():
    wak = "AIzaSyB49T25fdl4v4vNNycrlLISaRc2Op8-z-Y"  # Web Api Key

    def sign_up(self, email, password):
        app = App.get_running_app()
        email = email.replace("\n","")
        password = email.replace("\n","")
        # Send email and password to Firebase
        # Firebase will return localId, authToken (idToken), refreshToken
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        sign_up_data = json.loads(sign_up_request.content.decode())
        if sign_up_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            # Save refreshToken to a file
            with open(app.refresh_token_file, "w") as f:
                f.write(refresh_token)

            # Save localId to a variable in main app class
            # Save idToken to a variable in main app class
            app.local_id = localId
            app.id_token = idToken

            # Create new key in database from localId
            # Get friend ID
            # Get request on firebase to get the next friend id
            self.friend_get_req = UrlRequest("https://friendly-fitness.firebaseio.com/next_friend_id.json?auth=" + idToken, ca_file=certifi.where(), on_success=self.on_friend_get_req_ok, on_error=self.on_error, on_failure=self.on_error)

        elif sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]['message']
            if error_message == "EMAIL_EXISTS":
                self.sign_in_existing_user(email, password)
            else:
                app.root.ids['login_screen'].ids['login_message'].text = error_message.replace("_", " ")

    def on_error(self, req, result):
        print("FAILED TO GET USER DATA")
        print(result)

    def sign_in_existing_user(self, email, password):
        """Called if a user tried to sign up and their email already existed."""
        signin_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.wak
        signin_payload = {"email": email, "password": password, "returnSecureToken": True}
        signin_request = requests.post(signin_url, data=signin_payload)
        sign_up_data = json.loads(signin_request.content.decode())
        app = App.get_running_app()

        if signin_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            # Save refreshToken to a file
            with open(app.refresh_token_file, "w") as f:
                f.write(refresh_token)

            # Save localId to a variable in main app class
            # Save idToken to a variable in main app class
            app.local_id = localId
            app.id_token = idToken

            # Create new key in database from localId
            # Get friend ID
            # Get request on firebase to get the next friend id
            # --- User exists so i dont need to get a friend id
            #self.friend_get_req = UrlRequest("https://friendly-fitness.firebaseio.com/next_friend_id.json?auth=" + idToken, on_success=self.on_friend_get_req_ok)
            #app.change_screen("home_screen")
            app.on_start()
        elif signin_request.ok == False:
            error_data = json.loads(signin_request.content.decode())
            error_message = error_data["error"]['message']
            app.root.ids['login_screen'].ids['login_message'].text = "EMAIL EXISTS - " + error_message.replace("_", " ")


    def on_friend_get_req_ok(self, *args):
        app = App.get_running_app()
        my_friend_id = self.friend_get_req.result
        app.set_friend_id(my_friend_id)
        friend_patch_data = '{"next_friend_id": %s}' % (my_friend_id+1)
        friend_patch_req = UrlRequest("https://friendly-fitness.firebaseio.com/.json?auth=" + app.id_token,
                                          req_body=friend_patch_data, ca_file = certifi.where(), method='PATCH')


        # Update firebase's next friend id field
        # Default streak
        # Default avatar
        # Friends list
        # Empty workouts area
        my_data = '{"avatar": "man.png", "nicknames": {}, "friends": "", "workouts": "", "streak": "0", "my_friend_id": %s}' % my_friend_id
        post_request = UrlRequest("https://friendly-fitness.firebaseio.com/" + app.local_id + ".json?auth=" + app.id_token, ca_file=certifi.where(),
                       req_body=my_data, method='PATCH')

        app.change_screen("home_screen")

    def update_likes(self, friend_id, workout_key, likes, *args):
        app = App.get_running_app()
        friend_patch_data = '{"likes": %s}' % (likes)
        # Get their database entry based on their friend id so we can find their local ID
        check_req = requests.get('https://friendly-fitness.firebaseio.com/.json?orderBy="my_friend_id"&equalTo=' + friend_id)
        data = check_req.json()
        their_local_id = list(data.keys())[0]

        self.update_likes_patch_req = UrlRequest("https://friendly-fitness.firebaseio.com/%s/workouts/%s.json?auth="%(their_local_id, workout_key) + app.id_token,
                                          req_body=friend_patch_data, ca_file=certifi.where(), method='PATCH', on_success=self.update_likes_ok, on_failure=self.update_likes_ok)

    def update_likes_ok(self, *args):
        print(self.update_likes_patch_req.result)


    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id


if __name__ == '__main__':
    # example modified from the scrollview example

    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.garden.roulettescroll import RouletteScrollEffect
    from kivy.base import runTouchApp

    layout = GridLayout(cols=1, padding=10,
            size_hint=(None, None), width=500)

    layout.bind(minimum_height=layout.setter('height'))

    for i in range(30):
        btn = Button(text=str(i), size=(480, 40),
                     size_hint=(None, None))
        layout.add_widget(btn)

    root = ScrollView(size_hint=(None, None), size=(500, 320),
            pos_hint={'center_x': .5, 'center_y': .5}
            , do_scroll_x=False)
    root.add_widget(layout)

    root.effect_y = RouletteScrollEffect(anchor=20, interval=40)
    runTouchApp(root)