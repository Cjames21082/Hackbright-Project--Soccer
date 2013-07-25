from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy



app = Flask(__name__)
#create Flask obj
app.config.from_object('config')
# enable and read cross-site request forgery prevention
db = SQLAlchemy(app)




from app import views, model
