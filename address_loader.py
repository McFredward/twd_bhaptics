import pymeow
import time
import logging

def dprint(str,is_debug,logger):
    if(is_debug):
        logger.info(str)


def read_offsets(proc, base_adress, offsets):
    basepoint = pymeow.read_int64(proc,base_adress)
    current_pointer = basepoint
    for i in offsets[:-1]:
        current_pointer = pymeow.read_int64(proc,current_pointer+i)
    return current_pointer + offsets[-1]

def load_paused(process,base_addr,is_debug=False):
    pass

#loaded_adresses is either empty or contains all addresses in the returned
def load(process,base_addr,haptics_obj,logger,is_debug=False):

    ammo_base_adress1 = base_addr + 0x06347F20
    ammo_offsets1 = [0x30,0xDD8,0x120,0x128,0x0,0x5D0,0x110]

    ammo_base_adress2 = base_addr + 0x061E37F0
    ammo_offsets2 = [0x300,0x18,0x120,0x128,0x0,0x5D0,0x110]

    ammo_base_adress3 = base_addr + 0x0634C130
    ammo_offsets3 = [0x8, 0x8, 0x2E0, 0x560, 0x20, 0x58, 0x5C0]

    health_base_adress = base_addr + 0x06347DF8
    health_offsets = [0x48,0x20,0x918,0xB40,0x20,0xA8,0x810]

    #is_right_hand_base_address = base_addr + 0x061E37F0
    #is_right_hand_offsets = [0x30, 0x98, 0x2E8, 0x20, 0xA8, 0xD0, 0x5D4]

    #is_left_hand_base_address = base_addr + 0x06041460
    #is_left_hand_offsets = [0x8, 0x270, 0x110, 0x128, 0xB8, 0x5CC]

    is_both_hand_base_address = base_addr + 0x06347F20
    is_both_hand_offsets = [0x30, 0xDD8, 0x270, 0xA8, 0x1A8, 0x50, 0xE0]

    is_right_gun_base_address = base_addr + 0x06347F20
    is_right_gun_offsets = [0x30, 0xDD8, 0x278, 0xCE0, 0x330, 0x68, 0x2C]

    is_left_gun_base_address = base_addr + 0x06347F20
    is_left_gun_offsets = [0x30, 0xDD0, 0x278, 0xCE0, 0x330, 0x18, 0xE8]

    #old trigger offsets fired only if the button is more than half pressed in -> some shots are not recognized
    #right_trigger_pressed_base_address = base_addr + 0x062B80A8
    #right_trigger_pressed_offsets = [0x230, 0x8, 0x10, 0x30, 0x278]

    #left_trigger_pressed_base_address = base_addr + 0x05FFDF18
    #left_trigger_pressed_offsets = [0x230, 0x0, 0x30, 0x38]

    right_trigger_pressed_base_address = base_addr + 0x06352490
    right_trigger_pressed_offsets = [0x110]

    left_trigger_pressed_base_address = base_addr + 0x06352490
    left_trigger_pressed_offsets = [0x48]

    shoot_indicator_base_address = base_addr + 0x060BABA0
    shoot_indicator_offsets = [0x5B8, 0x40, 0x608, 0x660, 0x8, 0x78, 0x1C8]

    #buggy one which also fire sometimes if the player holds a gun with both hands
    #is_backpack_outside_base_address = base_addr + 0x062E54E8
    #is_backpack_outside_offsets = [0xF0,0x8,0x170,0xA40,0x1A0,0x8C]

    #Also fires if lamp or book is outside
    is_backpack_outside1_base_address = base_addr + 0x06347F20
    is_backpack_outside1_offsets = [0x30,0x2A0,0x128,0x8,0x1A8,0x110,0x330]

    #Also fires if one grabs an item out of the backpack (only the first time in a level) WEIRD!
    is_backpack_outside2_base_address = base_addr + 0x06347F20
    is_backpack_outside2_offsets = [0x30,0x290,0x128,0xF0,0x58,0x690,0x2DC]
    #Solution: Binary AND of both!

    #backpack_indicator_base_address = base_addr + 0x062A3C08
    #backpack_indicator_offsets = [0x90,0x38,0xA0,0x2D8,0x588]

    is_shoulder_packed1_base_address = base_addr + 0x061E37F0
    is_shoulder_packed1_offsets = [0x258,0x148,0xB8,0x98,0xA8,0xB8,0x47C]

    is_shoulder_packed2_base_address = base_addr + 0x06347F20
    is_shoulder_packed2_offsets = [0x30,0x290,0x2C8,0x138,0x128,0xD0,0x47C]

    #Buggy sometimes
    #zombie_attached_right_base_address = base_addr + 0x06347F20
    #zombie_attached_right_offsets = [0x30,0x2F0,0x20,0xA8,0xF8,0x268,0x198]

    zombie_attached_right_base_address = base_addr + 0x0634C130
    zombie_attached_right_offsets = [0x8,0x8,0x170,0x258,0xA8,0x268,0x198]

    zombie_attached_left_base_address = base_addr + 0x05F9B480
    zombie_attached_left_offsets = [0x8,0x78,0x28,0x8,0x170,0x240,0x1A8]

    endurance_base_address = base_addr + 0x06347DF8
    endurance_offsets = [0x40,0x20,0x268,0x20,0x978,0x20,0x814]

    is_eating_base_address = base_addr + 0x06347DF8
    is_eating_offsets = [0x120,0xB0,0x248,0x48,0x20,0x910,0x168]

    is_lamp_outside_base_address = base_addr + 0x0634A1D0
    is_lamp_outside_offsets = [0x0,0xA8,0x1A8,0x150,0x210,0x478,0x34]

    is_book_outside1_base_address = base_addr + 0x0634A1D0
    is_book_outside1_offsets = [0x0,0x20,0x128,0x10,0xD28,0x20,0x34]

    is_book_outside2_base_address = base_addr + 0x061E37F0
    is_book_outside2_offsets = [0x30,0xA8,0xD8,0x478,0xD28,0x20,0x34]

    is_book_outside3_base_address = base_addr + 0x06347F20
    is_book_outside3_offsets = [0x30,0x2E0,0x128,0x10,0xD28,0x20,0x34]

    stored_items_base_address = base_addr + 0x0634A1D0
    stored_items_offsets = [0x0,0x20,0x1A8,0x90,0xA8,0xB08]

    #is_left_stored_base_address = base_addr + 0x061E37F0
    #is_left_stored_offsets = [0x30,0x98,0x2B0,0x20,0xA8,0xC8,0x47C]

    is_left_stored_base_address = base_addr + 0x06347F20
    is_left_stored_offsets = [0x30,0x290,0x2C0,0x48,0x10,0x58,0x47C]

    #is_right_stored_base_address = base_addr + 0x060BB4A8
    #is_right_stored_offsets = [0xC8,0x40,0xB0,0x30,0xA8,0xD0,0x47C]

    is_right_stored2_base_address = base_addr + 0x061E37F0
    is_right_stored2_offsets = [0x30,0xA8,0xE8,0x490,0x128,0xB8,0x47C]

    is_right_stored1_base_address = base_addr + 0x060BA250
    is_right_stored1_offsets = [0x0,0x28,0x48,0x20,0x128,0xB8,0x47C]

    tries_count = 0
    while True:
        """
        #Doesnt work that way, address is not NULL but still readable. How to find out if the game closed?
        if(tries_count >= 100):
            try:
                a = process["modules"]["TWD-Win64-Shipping.exe"]["baseaddr"] #check if the game closed
                print("TEST: ", a)
            except:
                print("Game closed.")
                quit()
        """
        was_error = False
        try: #ammo has a bit more problems, some addresses work only in specific levels: test them all
            ammo_addr = read_offsets(process, ammo_base_adress1, ammo_offsets1)
        except:
            dprint("ammo_addr not found. Trying alternative..",is_debug,logger)
            try:
                ammo_addr = read_offsets(process, ammo_base_adress2, ammo_offsets2)
            except:
                dprint("ammo_addr not found. Trying alternative..", is_debug,logger)
                try:
                    ammo_addr = read_offsets(process, ammo_base_adress3, ammo_offsets3)
                except:
                    dprint("ammo_addr not found",is_debug,logger)
                    was_error = True
                    time.sleep(0.1)

        try:
            health_addr = read_offsets(process, health_base_adress, health_offsets)
        except:
            dprint("health_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            zombie_attached_right_addr = read_offsets(process, zombie_attached_right_base_address, zombie_attached_right_offsets)
        except:
            dprint("zombie_attached_right_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            zombie_attached_left_addr = read_offsets(process, zombie_attached_left_base_address, zombie_attached_left_offsets)
        except:
            dprint("zombie_attached_left_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_both_hand_addr = read_offsets(process, is_both_hand_base_address, is_both_hand_offsets)
        except:
            dprint("is_both_hand_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_right_gun_addr = read_offsets(process, is_right_gun_base_address, is_right_gun_offsets)
        except:
            dprint("is_right_gun_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_left_gun_addr = read_offsets(process, is_left_gun_base_address, is_left_gun_offsets)
        except:
            dprint("is_left_gun_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            right_trigger_pressed_addr = read_offsets(process, right_trigger_pressed_base_address,
                                                right_trigger_pressed_offsets)
        except:
            dprint("right_trigger_pressed_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            left_trigger_pressed_addr = read_offsets(process, left_trigger_pressed_base_address,
                                                     left_trigger_pressed_offsets)
        except:
            dprint("left_trigger_pressed_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            shoot_indicator_addr = read_offsets(process, shoot_indicator_base_address,
                                                     shoot_indicator_offsets)
        except:
            dprint("shoot_indicator_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_backpack_outside1_addr = read_offsets(process, is_backpack_outside1_base_address,
                                                     is_backpack_outside1_offsets)
        except:
            dprint("is_backpack_outside1_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_backpack_outside2_addr = read_offsets(process, is_backpack_outside2_base_address,
                                                     is_backpack_outside2_offsets)
        except:
            dprint("is_backpack_outside2_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_shoulder_packed1_addr = read_offsets(process, is_shoulder_packed1_base_address,
                                                     is_shoulder_packed1_offsets)
        except:
            dprint("is_shoulder_packed1_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_shoulder_packed2_addr = read_offsets(process, is_shoulder_packed2_base_address,
                                                     is_shoulder_packed2_offsets)
        except:
            dprint("is_shoulder_packed2_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            endurance_addr = read_offsets(process, endurance_base_address,
                                                     endurance_offsets)
        except:
            dprint("endurance_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_eating_addr = read_offsets(process, is_eating_base_address,
                                                     is_eating_offsets)
        except:
            dprint("is_eating_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_lamp_outside_addr = read_offsets(process, is_lamp_outside_base_address,
                                                     is_lamp_outside_offsets)
        except:
            dprint("is_lamp_outside_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_book_outside_addr = read_offsets(process, is_book_outside1_base_address,
                                                     is_book_outside1_offsets)
        except:
            dprint("is_book_outside_addr not found. Trying alternative..",is_debug,logger)
            try:
                is_book_outside_addr = read_offsets(process, is_book_outside2_base_address,
                                                         is_book_outside2_offsets)
            except:
                dprint("is_book_outside_addr not found. Trying alternative again..", is_debug, logger)
                try:
                    is_book_outside_addr = read_offsets(process, is_book_outside3_base_address,
                                                        is_book_outside3_offsets)
                except:
                    dprint("is_book_outside_addr not found", is_debug, logger)
                    was_error = True
                    time.sleep(0.1)

        try:
            stored_items_addr = read_offsets(process, stored_items_base_address,
                                                     stored_items_offsets)
        except:
            dprint("stored_items_addr not found",is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_left_stored_addr = read_offsets(process, is_left_stored_base_address,
                                             is_left_stored_offsets)
        except:
            dprint("is_left_stored_addr not found", is_debug,logger)
            was_error = True
            time.sleep(0.1)

        try:
            is_right_stored_addr = read_offsets(process, is_right_stored1_base_address,
                                             is_right_stored1_offsets)
        except:
            dprint("is_right_stored_addr not found. Trying alternative..", is_debug, logger)
            try:
                is_right_stored_addr = read_offsets(process, is_right_stored2_base_address,
                                                    is_right_stored2_offsets)
            except:
                dprint("is_right_stored_addr not found", is_debug, logger)
                was_error = True
                time.sleep(0.1)

        # allow max 1 item to be kept from last iteration (probably health)
        #Otherwise assume it is in loading screen and keep trying to load
        if (not was_error):
            break
        else: #Stop all Threads
            haptics_obj.heartbeat_active = False
            haptics_obj.healing_active = False
            haptics_obj.zombie_attached_left_active = False
            haptics_obj.zombie_attached_right_active = False
            haptics_obj.endurance_low_active = False
            haptics_obj.is_eating_active = False

        tries_count += 1
        continue
    return [ammo_addr,health_addr,zombie_attached_right_addr,zombie_attached_left_addr,is_both_hand_addr,is_right_gun_addr,is_left_gun_addr,
            right_trigger_pressed_addr,left_trigger_pressed_addr,shoot_indicator_addr,is_backpack_outside1_addr,is_backpack_outside2_addr,
            is_shoulder_packed1_addr,is_shoulder_packed2_addr,endurance_addr,is_eating_addr,is_lamp_outside_addr,is_book_outside_addr,stored_items_addr,
            is_left_stored_addr,is_right_stored_addr]

