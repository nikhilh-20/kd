import pygame, argparse

class key_dy_init():
    def __init__(self):
        # Holds the input string (password)
        self.inputstr = ''
        # Used in conjunction to measuring the dwell time
        self.Td = 0
        # Used in conjunction to measuring the flight time
        self.Tf = 0
        # Holds the dwell time for each character
        self.dwell_elapsed = []
        # Holds the flight time between two consecutive characters
        self.flight_elapsed = []
        # Just an iterator variable
        self.index = 0
        # The maximum deviation from the ideal identification value
        # Constant to get that in line
        self.allowed_Y_deviation = 2
        self.allowed_X_deviation = 0.15
        # Inflection point for function
        self.inflection_point = 1.5
        # Slope of function after X_var = inflection_point
        self.function_slope = 6
        # A dictionary of user:ID_sum. This will
        # be useful when we will sort the ID values and we
        # would want the usernames to move accordingly as well
        self.Users_ID = {}
        self.Users_keyAffinity = {}
        # Weighted values for calculated ID values. Not sure how effective
        # this will be. We can probably modify these values for anomalies
        # High weights : Slow typers become more slow
        # Increasing Wf by large margins mostly wouldn't make sense
        self.Wd = 1;
        self.Wf = 1;
        # Password
        self.password = '.zoroBen1'
        self.dwellLength = len(self.password) + 1
        self.flightLength = len(self.password)

        self.i = 0
        # Username
        self.user = ''
        pygame.init()
        self.self_pygame = pygame.time.Clock()

        parser = argparse.ArgumentParser(description='Keystroke Dynamics for keyboard')
        parser.add_argument('-action', metavar = '[test|train]', type = str, nargs = 1, required = True, help = 'Action to take')
        parser.add_argument('-user', type = str, help = 'Training of script => Username of the person')
        parser.add_argument('-debug', action = 'store_true')
        parser.add_argument('-b_testing', action = 'store_true', help = 'benchmark data testing')
        self.args = parser.parse_args()

        print("Package initialized")
