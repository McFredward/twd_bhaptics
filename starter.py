import pymeow
import time
import address_loader
import logging
from haptics import haptics

#pip install websocket websocket-client

#2021.12.08 / build 218977-STAGE
"""
>>>>Current Problems and approximative workarounds<<<<<

- shoot_indicator is 1 for the whole time the gunshot is hearable 
  Dont recognizes shoots which are coming fast behind each other
  SOLUTION:
  Use ammo in addition to shoot_indicator to check if there are more than one shot

- ammo is only the value of the gun in focus (last grabbed one)
  If a player holds two guns and shoots with the first grabbed (unfocused) one it is NOT recognized
  Approximative SOLUTION:
  If the player holds a gun in both hands, shoot_indicator = 1 and ammo is decreasing: SHOOT
  If ammo is not decreasing recognize is as one shoot the whole shoot_indicator timespan long
  PROBLEM: No fast gunshots in the unfocused hand are recognized
  
- ammo is not reducing if the last shot is breaking the weapon in the hand
  SOLUTION: Check if is_gun sets to zero WHILE the shot_indicator is still true

You found better pointers or other strategies to solve these? Contact me in the bHaptics Discord!
(wasted a lot of hours to find one)
"""
if __name__ == '__main__':
    print("""\
    ┌┐ ╦ ╦┌─┐┌─┐┌┬┐┬┌─┐┌─┐  ╔╦╗╦ ╦╔╦╗
    ├┴┐╠═╣├─┤├─┘ │ ││  └─┐   ║ ║║║ ║║
    └─┘╩ ╩┴ ┴┴   ┴ ┴└─┘└─┘   ╩ ╚╩╝═╩╝
    A bHaptics integration mod into The Walking Dead Saints & Sinners 
    Made by McFredward
    Haptic designs by Florian Fahrenberger
    v.0.2.2
    """)
    IS_DEBUG = False

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler('twd.log', 'w'))
    if(IS_DEBUG):
        print = logger.info

    print("Initializing bHaptics connection..")
    try:
        hap = haptics()
        hap.register_files()
        player = hap.player
    except:
        print("Error while connecting to the bHaptics Player. Make sure it is running.")
        exit()
    print("Waiting for the game to start..")
    while True:
        try:
            process = pymeow.process_by_name("TWD-Win64-Shipping.exe")
            base_addr = process["modules"]["TWD-Win64-Shipping.exe"]["baseaddr"]
            break
        except:
            pass
        time.sleep(0.5)

    loaded_adresses = []
    if (loaded_adresses == []):
        for i in range(14): #15 different addresses used
            loaded_adresses.append(0)

    print("Waiting for values to appear..")
    #Initial loading of the adresses
    loaded_adresses = address_loader.load(process,base_addr,hap,logger,IS_DEBUG)
    ammo_addr, health_addr, zombie_attached_right_addr, zombie_attached_left_addr, is_both_hand_addr,\
    is_right_gun_addr, is_left_gun_addr,\
    right_trigger_pressed_addr, left_trigger_pressed_addr, shoot_indicator_addr, is_backpack_outside1_addr,\
    is_backpack_outside2_addr,is_shoulder_packed1_addr,is_shoulder_packed2_addr, endurance_addr, is_eating_addr, is_lamp_outside_addr, is_book_outside_addr, \
    stored_items_addr, is_left_stored_addr, is_right_stored_addr = tuple(loaded_adresses)
    print("Everything ok.")

    ammo = pymeow.read_int(process, ammo_addr)
    right_trigger_zero_count = 0 #recognize a upcoming 1 at least 7 zeros (0.14s) afterwards
    left_trigger_zero_count = 0 #recognize a upcoming 1 at least 7 zeros (0.14s) afterwards
    shoot_indicator_true_phase = False
    block_break_shot = False
    is_right_gun_memory = False
    is_left_gun_memory = False
    gun_focus = -1 # For two handed gun case: -1 undefined | 0 left | 1 right
    is_shoulder_packed1 = 1 if pymeow.read_int(process, is_shoulder_packed1_addr) != 0 else 0
    is_shoulder_packed2 = 1 if pymeow.read_int(process, is_shoulder_packed2_addr) != 0 else 0
    is_shoulder_packed_memory = is_shoulder_packed1 or is_shoulder_packed2
    is_backpack_outside_memory = 0
    health_memory = 1
    stored_items_memory = 1000
    is_left_stored_memory = False
    is_right_stored_memory = False
    healing_started = False
    is_backpack_out = False
    is_book_out = False
    is_lamp_out = False
    counter = 0
    ammo_old = -1
    while True:
        #Reload the adresses all 100 steps
        if(counter % 500 == 0):
            #Check if the game is still running
            address_loader.dprint("Rechecking all addresses..",IS_DEBUG,logger)
            # Load all adresses again
            loaded_adresses = address_loader.load(process, base_addr, hap, logger, IS_DEBUG)
            ammo_addr, health_addr, zombie_attached_right_addr, zombie_attached_left_addr, is_both_hand_addr, \
            is_right_gun_addr, is_left_gun_addr, \
            right_trigger_pressed_addr, left_trigger_pressed_addr, shoot_indicator_addr, is_backpack_outside1_addr, \
            is_backpack_outside2_addr, is_shoulder_packed1_addr, is_shoulder_packed2_addr, endurance_addr, is_eating_addr, is_lamp_outside_addr, is_book_outside_addr, \
            stored_items_addr, is_left_stored_addr, is_right_stored_addr = tuple(loaded_adresses)
            counter = 0

        """
        --------------------GUNS---------------------
        """
        try:
            is_left_gun = 1 if pymeow.read_int(process, is_left_gun_addr) != 0 else 0
            is_right_gun = 1 if pymeow.read_int(process, is_right_gun_addr) != 0 else 0
            is_both_hand = 1 if pymeow.read_int(process, is_both_hand_addr) != 0 else 0
            shoot_indicator = 1 if pymeow.read_int(process, shoot_indicator_addr) != 0 else 0 #a short phase during a shot
            ammo = pymeow.read_int(process, ammo_addr)
            is_right_trigger_pressed = 1 if pymeow.read_float(process, right_trigger_pressed_addr) > 0.3 else 0
            is_left_trigger_pressed = 1 if pymeow.read_float(process, left_trigger_pressed_addr) > 0.3 else 0
        except:
            address_loader.dprint("Failed to load GUN addresses. Force reload..",IS_DEBUG,logger)
            counter = 500
            continue
        #print("SI:"+str(shoot_indicator)+" SIG:"+str(is_right_gun)+" IRTP:"+str(is_right_trigger_pressed)+" A:"+str(ammo)+" AO:"+str(ammo_old))
        if(shoot_indicator):# there is some shot: now find out from where
            #print("is_right_gun:",is_right_gun,"is_right_trigger_pressed",is_right_trigger_pressed,"ammo < ammo_old",ammo < ammo_old)
            if(is_right_gun and is_right_trigger_pressed and ammo < ammo_old): #right shot
                if(is_both_hand):
                    print("SHOOT both with primary right")
                    player.submit_registered("RecoilHands_R")
                    player.submit_registered("RecoilArms_R")
                    player.submit_registered("RecoilPistolVest_R")
                    player.submit_registered_with_option("RecoilHands_L", "RecoilHands_L08",
                                                         scale_option={"intensity": 0.4, "duration": 1},
                                                         rotation_option={"offsetAngleX": 0, "offsetY": 0})
                    player.submit_registered_with_option("RecoilArms_L", "RecoilArms_R08",
                                                         scale_option={"intensity": 0.4, "duration": 1},
                                                         rotation_option={"offsetAngleX": 0, "offsetY": 0})
                    player.submit_registered_with_option("RecoilPistolVest_L", "RecoilPistolVest_L08",
                                                         scale_option={"intensity": 0.4, "duration": 1},
                                                         rotation_option={"offsetAngleX": 0, "offsetY": 0})
                else:
                    print("SHOOT right")
                    player.submit_registered("RecoilHands_R")
                    player.submit_registered("RecoilArms_R")
                    player.submit_registered("RecoilPistolVest_R")
                if(is_right_gun and is_left_gun):
                    gun_focus = 1 #right
                else:
                    gun_focus = -1 #undefined
            elif(is_left_gun and is_left_trigger_pressed and ammo < ammo_old): #left shot
                if (is_both_hand):
                    print("SHOOT both with primary left")
                    player.submit_registered("RecoilHands_L")
                    player.submit_registered("RecoilArms_L")
                    player.submit_registered("RecoilPistolVest_L")
                    player.submit_registered_with_option("RecoilHands_R", "RecoilHands_L08",
                                                         scale_option={"intensity": 0.4, "duration": 1},
                                                         rotation_option={"offsetAngleX": 0, "offsetY": 0})
                    player.submit_registered_with_option("RecoilArms_R", "RecoilArms_R08",
                                                         scale_option={"intensity": 0.4, "duration": 1},
                                                         rotation_option={"offsetAngleX": 0, "offsetY": 0})
                    player.submit_registered_with_option("RecoilPistolVest_R", "RecoilPistolVest_L08",
                                                         scale_option={"intensity": 0.4, "duration": 1},
                                                         rotation_option={"offsetAngleX": 0, "offsetY": 0})
                else:
                    print("SHOOT left")
                    player.submit_registered("RecoilHands_L")
                    player.submit_registered("RecoilArms_L")
                    player.submit_registered("RecoilPistolVest_L")
                if(is_right_gun and is_left_gun):
                    gun_focus = 0 #left
                else:
                    gun_focus = -1 #undefined
            elif(is_left_gun and is_right_gun): #prolematic case: player (with two guns) shoots with the unfocused gun.
                if (not shoot_indicator_true_phase):
                    #print("SHOOT with unfocused gun")
                    if (is_right_trigger_pressed and not gun_focus == 1):
                        print("SHOOT right")
                        player.submit_registered("RecoilHands_R")
                        player.submit_registered("RecoilArms_R")
                        player.submit_registered("RecoilPistolVest_R")
                    elif (is_left_trigger_pressed and not gun_focus == 0):
                        print("SHOOT left")
                        player.submit_registered("RecoilHands_L")
                        player.submit_registered("RecoilArms_L")
                        player.submit_registered("RecoilPistolVest_L")
                    shoot_indicator_true_phase = True
            elif(is_right_trigger_pressed):#problematic case for the last shot when the gun breaks
                if(is_right_gun):
                    is_right_gun_memory = True
                else:
                    if(is_right_gun_memory):# gun vanishes of hand while a shot and ammo not changing -> break shot!
                        if (is_both_hand):
                            print("BREAK SHOOT both with primary right")
                            player.submit_registered("RecoilHands_R")
                            player.submit_registered("RecoilArms_R")
                            player.submit_registered("RecoilPistolVest_R")
                            player.submit_registered_with_option("RecoilHands_L", "RecoilHands_L08",
                                                                 scale_option={"intensity": 0.4, "duration": 1},
                                                                 rotation_option={"offsetAngleX": 0, "offsetY": 0})
                            player.submit_registered_with_option("RecoilArms_L", "RecoilArms_R08",
                                                                 scale_option={"intensity": 0.4, "duration": 1},
                                                                 rotation_option={"offsetAngleX": 0, "offsetY": 0})
                            player.submit_registered_with_option("RecoilPistolVest_L", "RecoilPistolVest_L08",
                                                                 scale_option={"intensity": 0.4, "duration": 1},
                                                                 rotation_option={"offsetAngleX": 0, "offsetY": 0})
                        else:
                            print("BREAK SHOOT right")
                            player.submit_registered("RecoilHands_R")
                            player.submit_registered("RecoilArms_R")
                            player.submit_registered("RecoilPistolVest_R")
                        is_right_gun_memory = False
            elif(is_left_trigger_pressed):#problematic case for the last shot when the gun breaks
                if(is_left_gun):
                    is_left_gun_memory = True
                else:
                    if(is_left_gun_memory):# gun vanishes of hand while a shot and ammo not changing -> break shot!
                        if (is_both_hand):
                            print("BREAK SHOOT both with primary left")
                            player.submit_registered("RecoilHands_L")
                            player.submit_registered("RecoilArms_L")
                            player.submit_registered("RecoilPistolVest_L")
                            player.submit_registered_with_option("RecoilHands_R", "RecoilHands_L08",
                                                                 scale_option={"intensity": 0.4, "duration": 1},
                                                                 rotation_option={"offsetAngleX": 0, "offsetY": 0})
                            player.submit_registered_with_option("RecoilArms_R", "RecoilArms_R08",
                                                                 scale_option={"intensity": 0.4, "duration": 1},
                                                                 rotation_option={"offsetAngleX": 0, "offsetY": 0})
                            player.submit_registered_with_option("RecoilPistolVest_R", "RecoilPistolVest_L08",
                                                                 scale_option={"intensity": 0.4, "duration": 1},
                                                                 rotation_option={"offsetAngleX": 0, "offsetY": 0})
                        else:
                            print("BREAK SHOOT left")
                            player.submit_registered("RecoilHands_L")
                            player.submit_registered("RecoilArms_L")
                            player.submit_registered("RecoilPistolVest_L")
                        is_left_gun_memory = False
        else:
            shoot_indicator_true_phase = False

        """
        --------------------Damage and Healing--------------------
        """
        try:
            health = pymeow.read_float(process, health_addr)
            endurance = pymeow.read_float(process, endurance_addr)
            zombie_attached_right = 1 if pymeow.read_int(process, zombie_attached_right_addr) != 0 else 0
            zombie_attached_left = 1 if pymeow.read_int(process, zombie_attached_left_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load DAMAGE addresses. Force reload..",IS_DEBUG,logger)
            counter = 500 #forces reload
            continue

        if(zombie_attached_right and not hap.zombie_attached_right_active):
            print("Start zombie attached right")
            player.submit_registered("ZombieGrabArm_R")
            player.submit_registered("ZombieGrabVest_R")
            hap.zombie_attached_right_active = True
        elif(not zombie_attached_right and hap.zombie_attached_right_active):
            print("Stop zombie attached right")
            hap.zombie_attached_right_active = False

        if(zombie_attached_left and not hap.zombie_attached_left_active):
            print("Start zombie attached left")
            player.submit_registered("ZombieGrabArm_L")
            player.submit_registered("ZombieGrabVest_L")
            hap.zombie_attached_left_active = True
        elif(not zombie_attached_left and hap.zombie_attached_left_active):
            print("Stop zombie attached left")
            hap.zombie_attached_left_active = False


        if(health < health_memory and not (hap.zombie_attached_left_active or hap.zombie_attached_right_active)):
            print("Damage")
            player.submit_registered("BulletHit")
        elif(health > health_memory and not hap.healing_active):
            print("Start healing")
            hap.healing_active = True
        elif(health == health_memory and hap.healing_active and counter % 50 == 0): #needs a bit delay
            print("Stop healing")
            hap.healing_active = False

        #print(health)
        if(health <= 0.25 and health > 0 and not hap.heartbeat_active): #heartbeat on low health
            print("Start heartbeat")
            hap.heartbeat_active = True
        elif(health > 0.25 and hap.heartbeat_active):
            print("Stop heartbeat")
            hap.heartbeat_active = False

        if(endurance == 0 and not hap.endurance_low_active):
            print("Start low endurance")
            hap.endurance_low_active = True
        elif(endurance > 0.2 and hap.endurance_low_active):
            print("Stop low endurance")
            hap.endurance_low_active = False

        health_memory = health
        """
        --------------------MISC---------------------
        """
        try:
            is_shoulder_packed1 = 1 if pymeow.read_int(process, is_shoulder_packed1_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_shoulder_packed1. Set it to zero..",IS_DEBUG,logger)
            is_shoulder_packed1 = 0

        try:
            is_shoulder_packed2 = 1 if pymeow.read_int(process, is_shoulder_packed2_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_shoulder_packed2. Set it to zero..",IS_DEBUG,logger)
            is_shoulder_packed2 = 0

        try:
            is_backpack_outside1 = 1 if pymeow.read_int(process, is_backpack_outside1_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_backpack_outside1. Set it to zero..",IS_DEBUG,logger)
            is_backpack_outside1 = 0

        try:
            is_backpack_outside2 = 1 if pymeow.read_int(process, is_backpack_outside2_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_backpack_outside2. Set it to zero..",IS_DEBUG,logger)
            is_backpack_outside2 = 0

        try:
            is_eating = 1 if pymeow.read_int(process, is_eating_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_eating. Force reload..",IS_DEBUG,logger)
            counter = 500
            continue

        try:
            stored_items = pymeow.read_int(process, stored_items_addr)
        except:
            address_loader.dprint("Failed to load stored_items. Force reload..",IS_DEBUG,logger)
            counter = 500
            continue

        try:
            is_lamp_outside = 1 if pymeow.read_int(process, is_lamp_outside_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_lamp_outside. Force reload..",IS_DEBUG,logger)
            counter = 500
            continue

        try:
            is_book_outside = 1 if pymeow.read_int(process, is_book_outside_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_book_outside. Force reload..",IS_DEBUG,logger)
            counter = 500
            continue

        try:
            is_left_stored = 1 if pymeow.read_int(process, is_left_stored_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_left_stored. Force reload..",IS_DEBUG,logger)
            counter = 500
            continue

        try:
            is_right_stored = 1 if pymeow.read_int(process, is_right_stored_addr) != 0 else 0
        except:
            address_loader.dprint("Failed to load is_left_stored. Force reload..",IS_DEBUG,logger)
            counter = 500
            continue

        is_shoulder_packed = is_shoulder_packed1 or is_shoulder_packed2
        is_backpack_outside = is_backpack_outside1 or is_backpack_outside2


        if(is_backpack_outside and not is_backpack_out):
            print("Backpack out")
            player.submit_registered("BackpackRetrieve_L")
            is_backpack_out = True
        elif(not is_backpack_outside and is_backpack_out):
            print("Backpack in")
            player.submit_registered("BackpackStore_L")
            is_backpack_out = False

        if(stored_items > stored_items_memory and not is_backpack_out and not (is_shoulder_packed > is_shoulder_packed_memory) and not \
          (is_left_stored and not is_left_stored_memory) and not (is_right_stored and not is_right_stored_memory)
          and not (ammo_old < ammo)):
            print("Item stored")
            player.submit_registered("ItemStore_L")

        stored_items_memory = stored_items
        is_left_stored_memory = is_left_stored
        is_right_stored_memory = is_right_stored

        if(is_shoulder_packed > is_shoulder_packed_memory):
            print("Shoulder packed in")
            player.submit_registered("BackpackStore_R")
            is_shoulder_packed_memory = is_shoulder_packed
        elif(is_shoulder_packed < is_shoulder_packed_memory):
            print("Shoulder packed out")
            player.submit_registered("BackpackRetrieve_R")
            is_shoulder_packed_memory = is_shoulder_packed

        #eating and endruance are correlated. Approx. solution: Only eat if endurance is full
        if(is_eating and not hap.is_eating_active):
            print("Start eating")
            hap.is_eating_active = True
        elif(not is_eating and hap.is_eating_active):
            print("Stop eating")
            hap.is_eating_active = False

        if(is_lamp_outside and not is_lamp_out):
            print("Lamp packed out")
            player.submit_registered("LampOut")
            is_lamp_out = True
        elif(not is_lamp_outside and is_lamp_out):
            print("Lamp packed in")
            player.submit_registered("LampOut")
            is_lamp_out = False

        if(is_book_outside and not is_book_out):
            print("Book packed out")
            player.submit_registered("BookOut")
            is_book_out = True
        elif(not is_book_outside and is_book_out):
            print("Book packed in")
            player.submit_registered("BookOut")
            is_book_out = False

        ammo_old = ammo
        counter += 1
        time.sleep(0.001)