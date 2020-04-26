import pyrebase


class Fire:

    def __init__(self):
        config = {
            "apiKey": "AIzaSyD82ifIkRwBFiWSaoRmly4P2-ehnxY1gWM",
            "authDomain": "podiatryvoice-b70a1.firebaseapp.com",
            "databaseURL": "https://podiatryvoice-b70a1.firebaseio.com",
            "projectId": "podiatryvoice-b70a1",
            "storageBucket": "podiatryvoice-b70a1.appspot.com",
            "messagingSenderId": "691483907965"
            }

        self.firebase = pyrebase.initialize_app(config)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

fire = Fire()

fire.auth.sign_in_anonymous()

print (fire)
