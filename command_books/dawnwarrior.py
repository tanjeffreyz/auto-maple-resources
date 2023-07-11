"""A collection of all commands that Shadower can use to interact with the game. 	"""
# UPDATED 3/17/2023

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up
import random
import pyautogui as pag
pag.PAUSE = 0.001


# List of key mappings
class Key:
    # Movement
    JUMP = 'space' 
    FLASH_JUMP = 'space' 
    EQUINOX_SLASH = 'shift'
    ROPE_LIFT = 'v'

    # Buffs
    CALL_OF_CYGNUS = '2' 
    GLORY_OF_THE_GUARDIANS = '3'
    SPEED_INFUSION = '6'
    HOLY_SYMBOL = '7'

    # Skills
    SOLARSLASH_LUNADIVIDE = 'e' 
    SOUL_ECLIPSE = 'f'
    COSMIC_SHOWER = 'q'
    ARACHNID = 'h' 
    ERDA_SHOWER = 'c'
    COSMOS = 'a'

#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 2
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if abs(d_y) > settings.move_tolerance * 1:
        if direction == 'down':
            press(Key.JUMP, 3)
        elif direction == 'up':
            press(Key.JUMP, 2)
    press(Key.FLASH_JUMP, num_presses)
    print("Jump")
    press(Key.SOLARSLASH_LUNADIVIDE, 1)
    press(Key.EQUINOX_SLASH, 1)
    print("Attack")
    time.sleep(0.5)

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=15):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = settings.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(0.01)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(0.01)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        FlashJump('up').main()
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Buff(Command):
    """Uses each of Shadowers's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.cd90_buff_time = 0
        self.cd120_buff_time = 0
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        #decent skills in buffs
        buffs = [Key.SPEED_INFUSION, Key.HOLY_SYMBOL]
        now = time.time()
        
        if self.cd90_buff_time == 0 or now - self.cd90_buff_time > 90:
            press(Key.COSMOS, 2)
            self.cd90_buff_time = now
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 120:
            press(Key.GLORY_OF_THE_GUARDIANS, 2)
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
            press(Key.SOUL_ECLIPSE, 2)
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now 
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
	        self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
	        press(Key.CALL_OF_CYGNUS, 2)
	        self.cd900_buff_time = now
        if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
	        for key in buffs:
		        press(key, 3, up_time=0.3)
	        self.decent_buff_time = now	

			
class FlashJump(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(0.1)
        press(Key.FLASH_JUMP, 1)
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1)
        key_up(self.direction)
        time.sleep(0.5)
			

class Attack(Command):
    """Uses 'Solar Slash/Luna Divide' once."""
        
    def main(self):
            press(Key.SOLARSLASH_LUNADIVIDE, 2)

class ErdaShower(Command):
    """
    Use ErdaShower in a given direction, Placing ErdaFountain if specified. Adds the player's position
    to the current Layout if necessary.
    """

    def __init__(self, direction, jump='False'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        num_presses = 3
        time.sleep(0.05)
        if self.direction in ['up', 'down']:
            num_presses = 2
        if self.direction != 'up':
            key_down(self.direction)
            time.sleep(0.05)
        if self.jump:
            if self.direction == 'down':
                press(Key.JUMP, 3, down_time=0.1)
            else:
                press(Key.JUMP, 1)
        if self.direction == 'up':
            key_down(self.direction)
            time.sleep(0.05)
        press(Key.ERDA_SHOWER, num_presses)
        key_up(self.direction)
        if settings.record_layout:
	        config.layout.add(*config.player_pos)


class SoulEclipse(Command):
    """Uses 'Soul Eclipse' once."""
        
    def main(self):
            press(Key.SOUL_ECLIPSE, 2)


class Cosmos(Command):
    """Uses 'Cosmos' once."""
        
    def main(self):
            press(Key.COSMOS, 2)

class Arachnid(Command):
    """Uses 'True Arachnid Reflection' once."""

    def main(self):
        press(Key.ARACHNID, 3)

class CosmicShower(Command):
    """Uses 'Cosmic Shower' once."""

    def main(self):
        press(Key.COSMIC_SHOWER, 2)

class EquinoxSlash(Command):
    """Uses 'Equinox Slash' once."""

    def main(self):
        press(Key.EQUINOX_SLASH, 2)	

class RopeLift(Command):
    """Uses 'Rope Lift' once."""

    def main(self):
        press(Key.ROPE_LIFT, 2)
