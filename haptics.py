from bhaptics import better_haptic_player as player
import os
from threading import *
import time
import random

class haptics:
    def __init__(self):
        self.player = player
        self.heartbeat_active = False
        self.healing_active = False
        self.zombie_attached_left_active = False
        self.zombie_attached_right_active = False
        self.endurance_low_active = False
        self.is_eating_active = False
        player.initialize()
        heartbeat_thread = Thread(target=self.heartbeat, daemon=True)
        heartbeat_thread.start()
        healing_thread = Thread(target=self.healing, daemon=True)
        healing_thread.start()
        zombie_attached_left_thread = Thread(target=self.zombie_attached_left, daemon=True)
        zombie_attached_left_thread.start()
        zombie_attached_right_thread = Thread(target=self.zombie_attached_right, daemon=True)
        zombie_attached_right_thread.start()
        endurance_low_thread = Thread(target=self.endurance_low, daemon=True)
        endurance_low_thread.start()
        is_eating_thread = Thread(target=self.is_eating, daemon=True)
        is_eating_thread.start()

    def heartbeat(self):
        while True:
            if(self.heartbeat_active):
                player.submit_registered("HeartBeat")
            time.sleep(1)

    def healing(self):
        while True:
            if(self.healing_active):
                player.submit_registered("Healing")
            time.sleep(2)

    def zombie_attached_left(self):
        while True:
            time.sleep(1)
            if(self.zombie_attached_left_active):
                player.submit_registered("ZombieHoldArm_L")

    def zombie_attached_right(self):
        while True:
            time.sleep(1)
            if(self.zombie_attached_right_active):
                player.submit_registered("ZombieHoldArm_R")

    def endurance_low(self):
        while True:
            if(self.endurance_low_active):
                player.submit_registered("LungContraction2")
            time.sleep(random.randint(800,2000) * 1e-3)

    def is_eating(self):
        while True:
            if(self.is_eating_active):
                player.submit_registered("Eating")
            time.sleep(1.6)

    def register_files(self):
        path = os.getcwd() + "/tact_files/"
        for filename in os.listdir(path):
            name = filename.split('.')[0]
            player.register(name, os.path.join(path, filename))
