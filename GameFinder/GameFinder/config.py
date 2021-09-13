import os


#class Config:
    # environ variables here
def get_key():
    SECRET_KEY = os.environ.get('GAMEFINDERSECRETKEY')
    return SECRET_KEY
