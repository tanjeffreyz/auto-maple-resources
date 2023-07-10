"""A collection of all commands that Luminous can use to interact with the game. 	"""
# Work In Progress


from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up
import pyautogui as pag
pag.PAUSE = 0.001

# List of key mappings
class Key:
    # Movement
    JUMP = 'space' 
    TELEPORT = 'shift' 
    FLASH_BLINK = 'w'
    ROPE_LIFT = 'v'

    # Buffs
    MAPLE_WARRIOR = '2' 
    HEROIC_MEMORIES = '3'
    SPEED_INFUSION = '8'
    HOLY_SYMBOL = '4'
    SHARP_EYE = '5'
    COMBAT_ORDERS = '6'
    ADVANCED_BLESSING = '7'

    # Skills
    ARACHNID = 'g'    
    LUCIDSOUL =  'h'
    REFLECTION = 'e'
    ERDA_SHOWER = 'c'
    GATE = 't'
    AETHER = 'q'
    BAPTISM = 's'
    LIBORB = 'a'
    APOCALYPSE = 'r'
    EQUALIZE = 'g'



#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 1
    # if direction == 'up' or direction == 'down':
    #     num_presses = 1
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
        time.sleep(0.01)
    d_y = target[1] - config.player_pos[1]
    if abs(d_y) > settings.move_tolerance * 1.2:
        if direction == 'down':
            press(Key.JUMP, 1)
        elif direction == 'up':
            press(Key.JUMP, 1)
            press(Key.TELEPORT, 1)
    press(Key.REFLECTION, 1)
    press(Key.TELEPORT, 1)
    print("Commandbook.")


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        print("Adjust.")
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
                        Teleport('up').main()
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
    """Uses each of Luminous's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.cd120_buff_time = 0
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        buffs = [Key.SPEED_INFUSION, Key.HOLY_SYMBOL, Key.SHARP_EYE, Key.COMBAT_ORDERS, Key.ADVANCED_BLESSING]
        now = time.time()

        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 120:
	        self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
	        self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
	        self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
	        self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
	        self.cd900_buff_time = now
        if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
	        self.decent_buff_time = now		

			
class Teleport(Command):
    """
    Teleports in a given direction, jumping if specified. Adds the player's position
    to the current Layout if necessary.
    """

    def __init__(self, direction, jump='False'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        num_presses = 3
        time.sleep(0.01)
        if self.direction in ['up', 'down']:
            num_presses = 2
        if self.direction != 'up':
            key_down(self.direction)
            time.sleep(0.01)
        if self.jump:
            if self.direction == 'down':
                press(Key.JUMP, 3)
            else:
                press(Key.JUMP, 2)
        if self.direction == 'up':
            key_down(self.direction)
            time.sleep(0.01)
        press(Key.TELEPORT, num_presses)
        key_up(self.direction)
        if settings.record_layout:
            config.layout.add(*config.player_pos)


class ReflectionDirect(Command):
    """Attacks using 'Reflection' in a given direction."""

    def __init__(self, direction, attacks=2, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        # time.sleep(0.05)
        key_down(self.direction)
        # time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        for _ in range(self.repetitions):
            press(Key.REFLECTION, self.attacks)
        key_up(self.direction)
        if self.attacks > 2:
            time.sleep(0.3)
        else:
            time.sleep(0.01)
		
class Reflection(Command):
    """Uses 'Reflection' once."""

    def main(self):
        press(Key.REFLECTION, 2)	
   		
class FlashBlinkRandom(Command):
    """Uses 'FlashBlink' once."""

    def main(self):
        press(Key.FLASH_BLINK, 1)	

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

class GateOfLight(Command):
    """Uses 'Gate of Light' once."""

    def main(self):
        press(Key.GATE, 2)

class Arachnid(Command):
    """Uses 'True Arachnid Reflection' once."""

    def main(self):
        press(Key.ARACHNID, 3)

class LucidSoul(Command):
    """
    Places 'Lucid Soul Summon' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        press(Key.LUCIDSOUL, 2)

class FlashBlink(Command):
    """
    Uses 'FlashBlink' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        press(Key.FLASH_BLINK, 2)

class RopeLift(Command):
    """Uses 'Rope Lift' once."""

    def main(self):
        press(Key.ROPE_LIFT, 2)

class AetherConduit(Command):
    """Uses 'Aether Conduit' once."""

    def main(self):
        press(Key.AETHER, 2)

class Baptism(Command):
    """Uses 'Baptism of Light and Darkness' once."""

    def main(self):
        press(Key.BAPTISM, 2)

class LiberationOrb(Command):
    """Uses 'Liberation Orb' once."""

    def main(self):
        press(Key.LIBORB, 2)

class Apocalypse(Command):
    """Uses 'Apocalypse' once."""

    def main(self):
        press(Key.APOCALYPSE, 2)

class Equalize(Command):
    """Uses 'Equalize' once."""

    def main(self):
        press(Key.EQUALIZE, 3)        

class ApocalypseDirect(Command):
    """Attacks using 'Apocalypse' in a given direction."""

    def __init__(self, direction, attacks=1, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(0.05)
        key_down(self.direction)
        time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        for _ in range(self.repetitions):
            press(Key.APOCALYPSE, self.attacks)
        key_up(self.direction)
        if self.attacks > 2:
            time.sleep(0.3)
        else:
            time.sleep(0.01)
