
is_log_enabled: bool = False

# comment below added by AI sends to dead link; this code was actually inspired by my transposition of a GODOT state machine implementation, which can be found here: https://www.youtube.com/watch?v=QM9yytr2YL4&t=391s
# state machine implementation inspired by https://www.youtube.com/watch?v=HhLwqQYyHf8&t=1s&ab_channel=CodeMonkey
class State():
    def __init__(self):
        pass
    def enter(self):
        pass
    def exit(self):
        pass
    def update(self):
        pass
    def get_state_name(self):
        return ""

class StateMachine():
    def __init__(self):
        # set up state machine with empty states and a default state
        self.current_state = State()
        # dictionary of states for easy access during transitions
        self.states = {}
        print(self.states)
    
    # takes in a list of states to initialize the state machine with, and sets the first state in the list as the default state
    def start_machine(self, init_states = [State]):
        # add states to state machine's state dictionary for easy access during transitions
        for state in init_states:
            print(state.get_state_name())
            self.states[state.get_state_name()] = state
            print(self.states)

        # set current state to first state in list of states passed into start_machine function
        self.current_state = init_states[0]

        if is_log_enabled:
            print('starting state machine...')

        self.current_state.enter()
        print("state machine started with state:", self.current_state.get_state_name())


    def update(self):
        if self.current_state == None:
            print('no current state...')
        else:
            self.current_state.update()
        
    def transition(self, new_state_name):
        new_state: State = self.states.get(new_state_name)
        self.current_state_name = self.current_state.get_state_name()
        if new_state == None:
            print("attempting to transition to non existent state")
        elif new_state != self.current_state:
            self.current_state.exit()
            
            if is_log_enabled:
                print('exiting state...')
            
            self.current_state = self.states[new_state.get_state_name()]

            if is_log_enabled:
                print('entering new state...')

            self.current_state.enter()
        else:
            if is_log_enabled:
                print("attempt to transition to " + new_state_name + " ignored since it is the current state...")
    