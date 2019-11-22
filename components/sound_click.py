from resource import Resource
import random


class SoundClick(object):
    rotaryHorizontal = [
        "sounds/RotaryHorizontal/rotary_01.ogg",
        "sounds/RotaryHorizontal/rotary_02.ogg",
    ]
    rotaryVertical = [
        "sounds/RotaryVertical/rotary_01.ogg",
        "sounds/RotaryVertical/rotary_03.ogg",
    ]

    @staticmethod
    def play_horizontal():
        Resource.getInstance().get_sound(random.choice(SoundClick.rotaryHorizontal)).play()

    @staticmethod
    def play_vertical():
        Resource.getInstance().get_sound(random.choice(SoundClick.rotaryVertical)).play()
