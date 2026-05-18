from state_machine import *
from settings import *


# --- Player States ---

class PlayerIdleState(State):
    """Active when the player is not pressing any movement keys."""

    def __init__(self, player):
        self.player = player
        self.name = "idle"

    def get_state_name(self):
        return "idle"

    def enter(self):
        # reset tint to white when standing still
        self.player.image.fill(WHITE)

    def exit(self):
        pass

    def update(self):
        # keep image white each frame in case another state changed it
        self.player.image.fill(WHITE)
        keys = pg.key.get_pressed()


class PlayerMoveState(State):
    """Active while the player is moving."""

    def __init__(self, player):
        self.player = player
        self.name = "move"

    def get_state_name(self):
        return "move"

    def enter(self):
        self.player.image.fill(WHITE)

    def exit(self):
        pass

    def update(self):
        # tint green while moving so the state is visually obvious during dev
        self.player.image.fill(GREEN)
        keys = pg.key.get_pressed()


# --- Guard States ---

class GuardPatrolState(State):
    """Guard walks back and forth between its two patrol points."""

    def __init__(self, guard):
        self.guard = guard
        self.name = "patrol"

    def get_state_name(self):
        return "patrol"

    def enter(self):
        # restore normal guard color when returning to patrol
        self.guard.image.fill(GUARD_COLOR)

    def exit(self):
        pass

    def update(self):
        # step toward the current patrol waypoint
        self.guard.move_toward_target()

        # switch to alert state if the player enters the vision cone
        if self.guard.can_see_player():
            self.guard.state_machine.transition("alert")


class GuardAlertState(State):
    """Guard has spotted the player — triggers game over."""

    def __init__(self, guard):
        self.guard = guard
        self.name = "alert"

    def get_state_name(self):
        return "alert"

    def enter(self):
        # flash white as a visual cue that detection happened
        self.guard.image.fill(WHITE)
        # set the flag that main.py checks to trigger the game over screen
        self.guard.game.player_caught = True

    def exit(self):
        pass

    def update(self):
        # guard freezes in place once alert — game over is already queued
        pass