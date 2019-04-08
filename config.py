import os, socket

DEFAULT_CAPTION             = "RasPipBoy-3000 Mk IV"
DEFAULT_WIDTH               = 480
DEFAULT_HEIGHT              = 320
DEFAULT_FRAMERATE           = 60
DEFAULT_MAP_COORDS          = (-26.9065, -49.0819)
DEFAULT_USE_SOUND           = True
DEFAULT_USE_WIFI            = True
DEFAULT_TINT_COLOR          = (0, 200, 0)
DEFAULT_BACKGROUND_COLOR    = (0, 0, 0)
DEFAULT_ASSETS_FOLDER       = os.path.abspath("./assets")
DEFAULT_DOWNLOAD_FOLDER     = os.path.abspath("./download")

download_radio              = True
download_folder             = DEFAULT_DOWNLOAD_FOLDER
width                       = DEFAULT_WIDTH
height                      = DEFAULT_HEIGHT
fullscreen                  = False
use_blur                    = True
use_scanline                = True
background_color            = DEFAULT_BACKGROUND_COLOR
tint_color                  = DEFAULT_TINT_COLOR
assets_folder               = DEFAULT_ASSETS_FOLDER
skip_intro                  = True
radios                      = {
                "Wastland": "https://www.youtube.com/watch?v=5eAalHA1bAc",
                }

def is_connected():
    REMOTE_SERVER = "www.google.com"
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False
