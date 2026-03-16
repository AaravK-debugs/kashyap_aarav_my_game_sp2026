from state_machine import *
from settings import *

class PlayerIdleState(State):
    def __init__(self, player):
        self.player = player
        self.name = "idle"

    def get_state_name(self):
        return "idle"

    def enter(self):
        self.player.image.fill(WHITE)
        print('enter player idle state')

    def exit(self):
        print('exit player idle state')

    def update(self):
        # print('updating player idle state...')
        self.player.image.fill(WHITE)
        keys = pg.key.get_pressed()
        #if keys[pg.K_k]:
        #    print('transitioning to attack state...')
        #    self.player.state_machine.transition("attack")
            
class PlayerMoveState(State):
    def __init__(self, player):
        self.player = player
        self.name = "move"

    def get_state_name(self):
        return "move"

    def enter(self):
        self.player.image.fill(WHITE)
        print('enter player move state')

    def exit(self):
        print('exit player move state')

    def update(self):
        # print('updating player move state...')
        self.player.image.fill(GREEN)
        keys = pg.key.get_pressed()


# guard patrols back and forth between two points
class GuardPatrolState(State):
    def __init__(self, guard):
        self.guard = guard
        self.name = "patrol"

    def get_state_name(self):
        return "patrol"

    def enter(self):
        # set guard color to normal when patrolling
        self.guard.image.fill(GUARD_COLOR)

    def exit(self):
        pass

    def update(self):
        # move guard toward its current patrol target
        self.guard.move_toward_target()

        # check if guard can see the player
        if self.guard.can_see_player():
            self.guard.state_machine.transition("alert")


# guard has spotted the player — triggers game over
class GuardAlertState(State):
    def __init__(self, guard):
        self.guard = guard
        self.name = "alert"

    def get_state_name(self):
        return "alert"

    def enter(self):
        # flash white to signal detection
        self.guard.image.fill(WHITE)
        print('guard spotted the player!')
        # tell the game the player was caught
        self.guard.game.player_caught = True

    def exit(self):
        pass

    def update(self):
        # stay frozen in alert — game is over
        pass
  