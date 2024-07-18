import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'data.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SERPER_API_KEY = "0fc010a8b99c05f84bd349406b409887d99c416b"