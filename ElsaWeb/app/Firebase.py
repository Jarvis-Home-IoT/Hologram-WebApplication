import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyCQXJQhF2Z6KppjLpW5cIGHQLlkkRIzRwM",
    "authDomain": "jarvis-69329.firebaseapp.com",
    "databaseURL": "https://jarvis-69329.firebaseio.com",
    "projectId": "jarvis-69329",
    "storageBucket": "jarvis-69329.appspot.com",
    "messagingSenderId": "693111507728",
    "appId": "1:693111507728:web:583f4a1fd777d27ad0b395"
  }

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

db.child("name").push({"company": "google"})