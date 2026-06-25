import pygame
import random
import json
import base64
import os
import codecs
import math
from pygame.locals import *
from importlib import resources

def to_binary_str(s):
    '''binary encoder'''
    return ''.join(format(ord(c), '08b') for c in s)

def from_binary_str(b):
    '''binary decoder'''
    if len(b) % 8 != 0:
        raise ValueError("Binary string length must be divisible by 8")
    if not all(c in '01' for c in b):
        raise ValueError("Binary string must only contain 0s and 1s")
    
    chars = [chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8)]
    return ''.join(chars)

def encode_save(json_str):
    '''encodes using method under'''
    # Base64 encode
    b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    # Reverse
    rev = b64[::-1]
    # ROT13 encode
    rot = codecs.encode(rev, 'rot_13')
    # Binary encode
    binary = to_binary_str(rot)
    return binary.encode('utf-8')

def decode_save(encoded_bytes):
    '''decodes using method under'''
    # grabs code
    binary_str = encoded_bytes.decode('utf-8')
    # Binary decode
    rot = from_binary_str(binary_str)
    # ROT13 decode
    rev = codecs.decode(rot, 'rot_13')
    # Reverse
    b64 = rev[::-1]
    # Base64 decode
    json_str = base64.b64decode(b64).decode('utf-8')
    return json_str


def get_config_dir():
    '''Return platform-appropriate config directory'''
    return os.path.expanduser("~/.config/BlackDuck-v2")

def load_game(): # access save file -JSON
    '''loading save file - returns pat game data'''
    global savefile_value
    config_dir = get_config_dir()
    save_path = os.path.join(config_dir, "BlackDuck-v2.bin")
    try:
        with open(save_path, "rb") as f:
            encoded_bytes = f.read()
            json_str = decode_save(encoded_bytes)
            data = json.loads(json_str)
            savefile_value = 1
            return (data.get("Money", 0),
                    data.get("Chips", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]) # 1, 5, 10, 25, 50, 100, 250, 500, 1.000, 2.500, 5.000, 10.000, 25.000, 50.000, 100.000, 250.000, 500,000
                    )
                    
    except FileNotFoundError:
        savefile_value = 2
        return 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]
    except (ValueError, json.JSONDecodeError) as error:
        print(f"Corrupted save file - using defaults. Error: {error}")
        savefile_value = 3  
        return 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]

def save_game(money_value = None, chip_info = None):
    '''saving game data'''
    if money_value is None:
        money_value = MONEY
    if chip_info is None:
        chip_info = CHIPS

    data = {
        "Money": money_value,
        "Chips": chip_info
    }
    json_str = json.dumps(data)
    encoded_bytes = encode_save(json_str)
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    save_path = os.path.join(config_dir, "BlackDuck-v2.bin")
    with open(save_path, "wb") as f:
        f.write(encoded_bytes)

MONEY, CHIPS = load_game()

def cosd(x):
    return math.cos(math.radians(x))
def sind(x):
    return math.sin(math.radians(x))

class game_variable: # Game variables
    def __init__(self):
        self.displayWidth, self.displayHeight = 1200, 700
        self.display = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.bg_colour = (23, 74, 67)
        self._running = True

        self.chipRadius = 50
        self.chipPos = [600, 350]
        self.chipCirclePoints = []
        self.chipCirclePointsReverse = []

        self.count = True

        for delta in range (270, 301, 2):
            self.chipCirclePoints.append([
                (cosd(delta) * (self.chipRadius)) + (self.chipPos[0]), 
                (sind(delta) * (self.chipRadius)) + (self.chipPos[1])
            ])
        for delta in range (270, 301, 2):
            self.chipCirclePointsReverse.append([
                (cosd(delta) * (self.chipRadius - 10)) + (self.chipPos[0]), 
                (sind(delta) * (self.chipRadius - 10)) + (self.chipPos[1])
            ])
        
        self.chipCirclePointsReverse.reverse()
        for i in self.chipCirclePointsReverse:
            self.chipCirclePoints.append(i)
        '''
        self.chipCirclePoints.append(((cosd(270) * (self.chipRadius)) + (self.chipPos[0] ), (sind(270) * (self.chipRadius)) + (self.chipPos[1] )))
        self.chipCirclePoints.append(((cosd(300) * (self.chipRadius)) + (self.chipPos[0] +1), (sind(300) * (self.chipRadius)) + (self.chipPos[1] +1)))
        self.chipCirclePoints.append(((cosd(300) * (self.chipRadius - 10)) + (self.chipPos[0]), (sind(300) * (self.chipRadius - 10)) + (self.chipPos[1])))
        self.chipCirclePoints.append(((cosd(270) * (self.chipRadius - 10)) + (self.chipPos[0]), (sind(270) * (self.chipRadius - 10)) + (self.chipPos[1])))
        '''

GV = game_variable()

class game_objects:
    def chip_object(self):

        pygame.draw.circle(GV.display, (159, 27, 39), GV.chipPos, (GV.chipRadius))
        pygame.draw.polygon(GV.display, (255, 255, 255), GV.chipCirclePoints)

class game_functions:
    def move_chip(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GV._running = False
            pygame.display.flip()
            if event.type == pygame.MOUSEBUTTONDOWN:
                cursorPosx, cursorPosy = pygame.mouse.get_pos()

                CursorPos_CirclePosx = cursorPosx - (GV.chipPos[0])
                CursorPos_CirclePosy = cursorPosy - (GV.chipPos[1])

                CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2

                if CursorPos_CirclePos <= GV.chipRadius**2:
                    print("inside")
                    print(pygame.mouse.get_pos())
                else:
                    print("outside")

GF = game_functions()

class pygame_function:
    def __init__(self):
        self.fps = 60
        self.FPS = pygame.time.Clock()
        self.display = None

        GV._running = True
    def on_init(self):
        pygame.init()
        
        pygame.display.set_caption("BlackDuck v2")
        GV._running = True
    def starting_game(self):
        pass
    def game_starting(self):
        pass
    def on_event(self, event):
        if event.type == pygame.QUIT:
            GV._running = False
    def on_render(self):
        GV.display.fill(GV.bg_colour)
        game_objects.chip_object(self)
    def on_loop(self):
        pass
    def on_cleanup(self):
        pygame.quit()
    def on_execute(self):
        if self.on_init() == False:
            GV._running = False 
        while(GV._running):
            self.FPS.tick(self.fps)
            GF.move_chip()
            self.on_loop()
            self.on_render()
            pygame.display.flip()

def main():
    Game = pygame_function()
    Game.on_execute()

if __name__ == "__main__":
    main()
