from flask import Flask

#create Flask obj
app = Flask(__name__)

app.config.from_object('config')


from app import views, model

