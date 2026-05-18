# controls whether debug print statements are shown
is_log_enabled: bool = False

# inspired by a Godot state machine implementation:
# https://www.youtube.com/watch?v=QM9yytr2YL4&t=391s


class State:
    """Base class for all states. Subclasses override enter, exit, and update."""

    def __init__(self):
        pass

    def enter(self):
        # called once when the machine switches into this state
        pass

    def exit(self):
        # called once when the machine switches away from this state
        pass

    def update(self):
        # called every frame while this state is active
        pass

    def get_state_name(self):
        # returns a unique string key used to look up this state during transitions
        return ""


class StateMachine:
    def __init__(self):
        self.current_state = State()  # placeholder until start_machine is called
        self.states = {}              # name -> State lookup table

    def start_machine(self, init_states=[State]):
        # register every state in the dictionary by its name
        for state in init_states:
            self.states[state.get_state_name()] = state

        # first state in the list becomes the starting state
        self.current_state = init_states[0]
        self.current_state.enter()

        if is_log_enabled:
            print("state machine started with state:", self.current_state.get_state_name())

    def update(self):
        # delegate the frame update to whichever state is currently active
        if self.current_state is None:
            print('no current state...')
        else:
            self.current_state.update()

    def transition(self, new_state_name):
        # look up the target state by name
        new_state = self.states.get(new_state_name)

        if new_state is None:
            print("attempting to transition to non existent state")
        elif new_state != self.current_state:
            # exit the old state, then enter the new one
            self.current_state.exit()
            self.current_state = self.states[new_state.get_state_name()]
            self.current_state.enter()

            if is_log_enabled:
                print(f"transitioned to {new_state_name}")
        else:
            if is_log_enabled:
                print(f"transition to {new_state_name} ignored — already active")