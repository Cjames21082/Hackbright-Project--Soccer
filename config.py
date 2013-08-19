import os
import psycopg2


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2:///hackbright'
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'app.db')
# required globally- path to db


CSRF_ENABLED = True
SECRET_KEY = 'HAKHFAHFJSBASBDASJD'

#pagination
POSTS_PER_PAGE = 3
