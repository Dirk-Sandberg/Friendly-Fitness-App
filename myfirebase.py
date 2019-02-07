import requests
import json
from kivy.app import App

class MyFirebase():
    wak = "AIzaSyB49T25fdl4v4vNNycrlLISaRc2Op8-z-Y"  # Web Api Key

    def sign_up(self, email, password):
        app = App.get_running_app()
        # Send email and password to Firebase
        # Firebase will return localId, authToken (idToken), refreshToken
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        print(sign_up_request.ok)
        print(sign_up_request.content.decode())
        sign_up_data = json.loads(sign_up_request.content.decode())
        print(sign_up_data)
        if sign_up_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            # Save refreshToken to a file
            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)

            # Save localId to a variable in main app class
            # Save idToken to a variable in main app class
            app.local_id = localId
            app.id_token = idToken


            # Create new key in database from localId
            # Get friend ID
            # Get request on firebase to get the next friend id
            friend_get_req = requests.get("https://friendly-fitness.firebaseio.com/next_friend_id.json?auth=" + idToken)
            my_friend_id = friend_get_req.json()
            print(my_friend_id)
            friend_patch_data = '{"next_friend_id": %s}' % (my_friend_id+1)
            friend_patch_req = requests.patch("https://friendly-fitness.firebaseio.com/.json?auth=" + idToken,
                                              data=friend_patch_data)


            print("friend ", friend_get_req.json())
            # Update firebase's next friend id field
            # Default streak
            # Default avatar
            # Friends list
            # Empty workouts area
            my_data = '{"avatar": "man.png", "friends": "", "workouts": "", "streak": "0", "my_friend_id": %s}'% my_friend_id
            post_request = requests.patch("https://friendly-fitness.firebaseio.com/" + localId + ".json?auth=" + idToken,
                           data=my_data)
            print(post_request.ok)
            print(json.loads(post_request.content.decode()))

            app.change_screen("home_screen")

        if sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]['message']
            app.root.ids['login_screen'].ids['login_message'].text = error_message



        pass

    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        print("REFRESH OK?", refresh_req.ok)
        print(refresh_req.json())
        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id
