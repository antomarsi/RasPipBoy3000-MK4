import pygame, os, glob, json
# RasPipBoy: A Pip-Boy 3000 implementation for Raspberry Pi
#    Neal D Corbett, 2013
# Configuration data

# Device options 
#  (These will be automatically be set to 'False' if unavailable)
USE_INTERNET = False        # Download map/place data via internet connection
USE_GPS = False            # Use GPS module, accessed via GPSD daemon
USE_SOUND = True        # Play sounds via RasPi's current sound-source
USE_CAMERA = False        # Use RasPi camera-module as V.A.T.S
USE_SERIAL = False        # Communicate with custom serial-port controller

QUICKLOAD = False       # If true, commandline-startup bits aren't rendered
FORCE_DOWNLOAD = False    # Don't use cached map-data, if online

# Render screen-objects at this size - smaller is faster
WIDTH = 320
HEIGHT = 240
FULLSCREAN = False
DISPLAY_MODE = pygame.RESIZABLE
USE_SCANLINE = True
USE_BACKGROUND = False
POST_PROCESSING = True
BLINK = False
# Address for map's default position: 
#    (used if GPS is inactive)
defaultPlace = "Blumenau SC"

CHARACTER_JSON_FILE = "character.json"

ITEM_DATABASE = []
for f in glob.glob("data/*.json"):
    with open(f, "rb") as infile:
        ITEM_DATABASE += (json.load(infile))
FPS = 15

# My Google-API key:
# (this is limited to only 2000 location requests a day, 
#    so please don't use this key if you're making your own project!)
gKey = 'AIzaSyBE_AN9JYmRuBtb2qfwPBaT2dAumJmkm2I'


# Teensy USB serial: symbolic link set up by creating: 
#   /etc/udev/rules.d/99-usb-serial.rules
# With line:
#   SUBSYSTEM=="tty", ATTRS{manufacturer}=="Teensyduino", SYMLINK+="teensy"
SERIALPORT = '/dev/teensy'
# Pi GPIO serial:
#SERIALPORT = '/dev/ttyAMA0'

KEYS = {
    "UP":pygame.K_UP,
    "DOWN":pygame.K_DOWN,
    "LEFT":pygame.K_LEFT,
    "RIGHT":pygame.K_RIGHT,
    "SELECT":pygame.K_RETURN,
    "BACK":pygame.K_BACKSPACE,
    "NEXT_MENU":pygame.K_e,
    "PREVIUS_MENU":pygame.K_q,
    "NEXT_SUB":pygame.K_d,
    "PREVIUS_SUB":pygame.K_a,
    "FAVORITE":pygame.K_f,
    "QUIT":pygame.K_ESCAPE
}
# Test serial-controller:
if USE_SERIAL:
    # Load libraries used by serial device, if present:
    def loadSerial():
        try:
            print ("Importing Serial libraries...")
            global serial
            import serial
        except:
            # Deactivate serial-related systems if load failed:
            print ("SERIAL LIBRARY NOT FOUND!")
            USE_SERIAL = False
    loadSerial()
if(USE_SERIAL):
    try:
        print ("Init serial: %s" %(SERIALPORT))
        ser = serial.Serial(SERIALPORT, 9600)
        ser.timeout=1
        
        print ("  Requesting device identity...")
        ser.write("\nidentify\n")
        
        ident = ser.readline()
        ident = ident.strip()
        print ("    Value: %s" %(str(ident)))
        
        if (ident != "PIPBOY"):
            print ("Pip-Boy controls not found on serial-port!")
            #config.USE_SERIAL = False
        
    except:
        print ("* Failed to access serial! Ignoring serial port")
        USE_SERIAL = False
print ("SERIAL: %s" %(USE_SERIAL))

# Test camera:
if USE_CAMERA:
    # Is there a camera module connected?
    def hasCamera():
        try:
            import picamera
            camera = picamera.PiCamera()
            camera.close()
            return True
        except:
            return False
    
    USE_CAMERA = hasCamera()
print ("CAMERA: %s" %(USE_CAMERA))

# Downloaded/auto-generated data will be put here:
CACHEPATH = 'cache'
if not os.path.exists(CACHEPATH):
    os.makedirs(CACHEPATH)

DRAWCOLOUR = pygame.Color (255, 255, 255)
TINTCOLOUR = pygame.Color (0, 255, 0)
SELBOXGREY = 50

EVENTS = {
    'SONG_END': pygame.USEREVENT + 1
}

print("Loading images...")
IMAGES = {
    "background":pygame.image.load('assets/images/pipboy_back.png'),
    "scanline":pygame.image.load('assets/images/pipboyscanlines.png'),
    "distort":pygame.image.load('assets/images/pipboydistorteffectmap.png'),
    "statusboy":pygame.image.load('assets/images/pipboy_statusboy.png'),
    "status_page": {
        "damage": pygame.image.load('assets/icons/FO4StatsPageIcons/icon_3.png'),
        "water": pygame.image.load('assets/icons/FO4StatsPageIcons/icon_5.png'),
        "fire": pygame.image.load('assets/icons/FO4StatsPageIcons/icon_7.png'),
        "electric": pygame.image.load('assets/icons/FO4StatsPageIcons/icon_9.png'),
        "frost": pygame.image.load('assets/icons/FO4StatsPageIcons/icon_11.png'),
        "radiation": pygame.image.load('assets/icons/FO4StatsPageIcons/icon_13.png'),
        "armor": pygame.image.load('assets/icons/FO4StatsPageIcons/icon_154.png'),
    },
    "health_cond":{
        "Body":{
            "Normal":pygame.image.load('assets/img/health_cond/icon_condition_body_0.png'),
            "LeftArm":pygame.image.load('assets/img/health_cond/icon_condition_body_1.png'),
            "RightArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_2.png'),
            "BothArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_3.png'),
            "LeftLegload":pygame.image.load('assets/img/health_cond/icon_condition_body_4.png'),
            "LeftLegLeftArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_5.png'),
            "LeftLegRightArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_6.png'),
            "LeftLegBothArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_7.png'),
            "RightLegload":pygame.image.load('assets/img/health_cond/icon_condition_body_8.png'),
            "RightLegLeftArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_9.png'),
            "RightLegRightArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_10.png'),
            "RightLegBothArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_11.png'),
            "BothLegload":pygame.image.load('assets/img/health_cond/icon_condition_body_12.png'),
            "BothLegLeftArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_13.png'),
            "BothLegRightArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_14.png'),
            "BothLegBothArmload":pygame.image.load('assets/img/health_cond/icon_condition_body_15.png')
        },
        "Head": {
            "Normal": pygame.image.load('assets/img/health_cond/icon_condition_head_1.png'),
            "Poisoned": pygame.image.load('assets/img/health_cond/icon_condition_head_3.png'),
            "Addicted": pygame.image.load('assets/img/health_cond/icon_condition_head_5.png'),
            "Ghoul": pygame.image.load('assets/img/health_cond/icon_condition_head_7.png'),
            "NormalInjured": pygame.image.load('assets/img/health_cond/icon_condition_head_9.png'),
            "PoisonedInjured": pygame.image.load('assets/img/health_cond/icon_condition_head_9.png'),
            "AddictedInjured": pygame.image.load('assets/img/health_cond/icon_condition_head_11.png'),
            "GhoulInjured": pygame.image.load('assets/img/health_cond/icon_condition_head_13.png'),
        }
    },
    "damage_type": [
        pygame.image.load('assets/icons/FO4InvPageIcons/icon_206.png'),
        pygame.image.load('assets/icons/FO4InvPageIcons/icon_46.png'),
        pygame.image.load('assets/icons/FO4InvPageIcons/icon_40.png'),
        pygame.image.load('assets/icons/FO4InvPageIcons/icon_38.png'),
        pygame.image.load('assets/icons/FO4InvPageIcons/icon_42.png'),
        pygame.image.load('assets/icons/FO4InvPageIcons/icon_138.png'),
        pygame.image.load('assets/icons/FO4InvPageIcons/icon_140.png'),
        pygame.image.load('assets/icons/FO4InvPageIcons/icon_44.png')
    ]
}

print("(done)")

# Test internet connection:
if USE_INTERNET:
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
    
    def internet_on():
        req = Request('http://www.google.com')
        try:
            # Can we access this Google address?
            response = urlopen(req, timeout=5)
            return True
        except URLError as e: pass
        return False
    
    USE_INTERNET = internet_on()
print ("INTERNET: %s" %(USE_INTERNET))

# Test and set up sounds::
MINHUMVOL = 0.7
MAXHUMVOL = 1.0
if USE_SOUND:
    try:
        print ("Loading sounds...")
        pygame.mixer.init(44100, -16, 2, 2048)
        NEW_SOUNDS = {
            "BootSequence": [
                 pygame.mixer.Sound('assets/sounds/new/boot/a.ogg'),
                 pygame.mixer.Sound('assets/sounds/new/boot/b.ogg'),
                 pygame.mixer.Sound('assets/sounds/new/boot/c.ogg')
            ],
            "Up": [
                 pygame.mixer.Sound('assets/sounds/new/UpDown/up_1.ogg'),
                 pygame.mixer.Sound('assets/sounds/new/UpDown/up_2.ogg')
            ],
            "Loop": pygame.mixer.Sound('assets/sounds/new/UI_PipBoy_Hum_LP.wav'),
            "RotaryVertical": [
                pygame.mixer.Sound('assets/sounds/new/RotaryVertical/rotary_01.ogg'),
                pygame.mixer.Sound('assets/sounds/new/RotaryVertical/rotary_03.ogg')
            ],
            "RotaryHorizontal": [
                pygame.mixer.Sound('assets/sounds/new/RotaryHorizontal/rotary_01.ogg'),
                pygame.mixer.Sound('assets/sounds/new/RotaryHorizontal/rotary_02.ogg')
            ],
            "LightOn": [pygame.mixer.Sound('assets/sounds/new/UI_PipBoy_LightOn.ogg')],
            "LightOff": [pygame.mixer.Sound('assets/sounds/new/UI_PipBoy_LightOff.ogg')],
            "BurstDriveA": [
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_01.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_02.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_03.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_04.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_05.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_06.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_07.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_08.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_09.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_10.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_11.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_12.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_13.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_14.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_15.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_16.ogg'),
                pygame.mixer.Sound('assets/sounds/new/BurstDriveA/bustdrivea_17.ogg'),
            ]
        }
        SOUNDS["hum"].set_volume(MINHUMVOL)
        print ("(done)")
    except:
        USE_SOUND = False
print ("SOUND: %s" %(USE_SOUND))

# Set up fonts:
pygame.font.init()
kernedFontName = 'assets/fonts/monofonto-kerned.ttf'
monoFontName = 'assets/fonts/monofonto.ttf'

# Scale font-sizes to chosen resolution:
FONT_SML = pygame.font.Font(kernedFontName, int (HEIGHT * (12.0 / 360)))
FONT_MED = pygame.font.Font(kernedFontName, int (HEIGHT * (16.0 / 360.0)))
FONT_LRG = pygame.font.Font(kernedFontName, int (HEIGHT * (24.0 / 360.0)))
MONOFONT = pygame.font.Font(monoFontName, int (HEIGHT * (16.0 / 360.0)))

# Find monofont's character-size:
tempImg = FONT_SML.render("X", True, DRAWCOLOUR, (0, 0, 0))
SMLcharHeight = tempImg.get_height()
SMLcharWidth = tempImg.get_width()


tempImg = FONT_MED.render("X", True, DRAWCOLOUR, (0, 0, 0))
MEDcharHeight = tempImg.get_height()
MEDcharWidth = tempImg.get_width()


tempImg = FONT_LRG.render("X", True, DRAWCOLOUR, (0, 0, 0))
LRGcharHeight = tempImg.get_height()
LRGcharWidth = tempImg.get_width()


# Find monofont's character-size:
tempImg = MONOFONT.render("X", True, DRAWCOLOUR, (0, 0, 0))
charHeight = tempImg.get_height()
charWidth = tempImg.get_width()
del tempImg