import termios, sys, time, math, csv, re, subprocess, argparse, operator, os
from random import randint
from collections import Counter
import collections
import pygame 
from pygame.locals import *

class KeyDynamics:
    
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
        # GUI flag - to store values in a different file
        self.gui = 0
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

    def findEstimates(self, allowedVariation, fileValues=[]):
        if (self.args.debug):
            print ("findEstimates")

        valuesDict = {}
        maxKeys = []
        sumKeys = 0.0
        estimate = 0.0

        # Initializing dictionary keys=>values
        for i in range(0,len(fileValues)):
            valuesDict['k'+str(fileValues[i])] = 0

        fileValues.sort()

        for i in fileValues:
            for j in fileValues:
                if (abs(float(i)-float(j)) <= allowedVariation):
                    valuesDict['k'+str(i)] += 1

        for i in valuesDict:
            maxKey = i
            for j in valuesDict:
                if (valuesDict[maxKey] < valuesDict[j]):
                    maxKey = j
            if (maxKey in maxKeys):
                next
            else:
                maxKeys.append(maxKey)

        for i in maxKeys:
            sumKeys += float(i[1:])

        estimate = sumKeys/len(maxKeys)
        deviationEstimate = self.findDeviationEstimate(estimate, fileValues)
        return (estimate, deviationEstimate)

    def findDeviationEstimate(self, mean, arr=[]):
        if (self.args.debug):
            print ("findDeviationEstimate")

        sum = 0.0

        for value in arr:
            sum += math.pow((float(value) - mean),2)

        deviation = math.sqrt(sum/len(arr))
        return deviation

    def GDP(self, inputType, referenceMean=[], referenceDeviation=[], featureInput=[]):
        if (self.args.debug):
            print ("GDP")

        sumValues = 0.0
        scoreDict = {} 
        checkValue = [0] * len(referenceMean)

        for indexOuter in range(0, len(referenceMean)):
            checkValue[indexOuter] = 0
            for indexInner in range(0, len(referenceMean[indexOuter])):
                diff = abs(float(featureInput[indexInner]) - float(referenceMean[indexOuter][indexInner]))
                if (str(inputType) == 'dwell'):
                    if (diff <= 1.25 * float(referenceDeviation[indexOuter][indexInner])):
                        checkValue[indexOuter] += 1
                elif (str(inputType) == 'flight'):
                    if (diff <= float(referenceDeviation[indexOuter][indexInner])):
                        checkValue[indexOuter] += 1
                else:
                    print ("Couldn't recognize type of input")
                    exit()
                sumValues += diff
            scoreDict['k' + str(indexOuter)] = (sumValues)
            sumValues = 0.0

        return (checkValue, scoreDict)

    # All input arguments are for input
    def findMatch(self, action, keyAffinity, dwell=[], flight=[]):
        if (self.args.debug):
            print ("findMatch")

        if (len(dwell) != self.dwellLength or len(flight) != self.flightLength):
            print ("Weird... I couldn't extract the information I need. Please retry.")
            exit()

        if (self.args.b_testing):
            with open ('benchmark/dwellMean.csv' , 'rt') as f:
                reader = csv.reader(f)    
                dwellMean = list(reader) 
            with open ('benchmark/dwellDeviation.csv' , 'rt') as f:
                reader = csv.reader(f)
                dwellDeviation = list(reader)
            with open ('benchmark/flightMean.csv' , 'rt') as f:
                reader = csv.reader(f)
                flightMean = list(reader)
            with open ('benchmark/flightDeviation.csv' , 'rt') as f:
                reader = csv.reader(f)
                flightDeviation = list(reader)
            with open ('benchmark/users_Converged.csv' , 'rt') as f:
                reader = csv.reader(f)
                Users = list(reader)
            with open ('benchmark/key_keyboard_values.csv' , 'rt') as f:
                reader = csv.reader(f)
                keyAffinity_ofUser = list(reader) 
        else:
            with open ('dwellFlightkeyboard/dwellMean.csv' , 'rt') as f:
                reader = csv.reader(f)
                dwellMean = list(reader)
            with open ('dwellFlightkeyboard/dwellDeviation.csv' , 'rt') as f:
                reader = csv.reader(f)
                dwellDeviation = list(reader)
            with open ('dwellFlightkeyboard/flightMean.csv' , 'rt') as f:
                reader = csv.reader(f)
                flightMean = list(reader)
            with open ('dwellFlightkeyboard/flightDeviation.csv' , 'rt') as f:
                reader = csv.reader(f)
                flightDeviation = list(reader)
            with open ('dwellFlightkeyboard/users_Converged.csv' , 'rt') as f:
                reader = csv.reader(f)
                Users = list(reader)
            with open ('dwellFlightkeyboard/key_keyboard_values.csv' , 'rt') as f:
                reader = csv.reader(f)
                keyAffinity_ofUser = list(reader)
        
        # Correcting the format of the array
        for index in range(0,len(keyAffinity_ofUser)):
            keyAffinity_ofUser[index] = keyAffinity_ofUser[index][0]

        (checkDwellValue, scoreDwellDict) = self.GDP('dwell', dwellMean, dwellDeviation, dwell)
        (checkFlightValue, scoreFlightDict) = self.GDP('flight', flightMean, flightDeviation, flight)
        self.findUserMatch(keyAffinity, Users, keyAffinity_ofUser, checkDwellValue, checkFlightValue, scoreDwellDict, scoreFlightDict)

    # Input - dwell/flight of all and keep track of how many times they were under standard deviation
    def findUserMatch(self, keyAffinity, Users=[], keyAffinityOfUsers=[], checkDwellValue=[], checkFlightValue=[], dwellScore={}, flightScore={}):
        if (self.args.debug):
            print ("findUserMatch")

        score = {}
        score2 = {}
        minKey = 'k0'
        minScore = {minKey : 100}
        sumReference = []
        found = 0
        finalScore = {}

        for index in dwellScore:
            dwell_weight = self.dwellLength - checkDwellValue[int(index[1:])]
            flight_weight = self.flightLength - checkFlightValue[int(index[1:])]
            if (int(dwell_weight) == 0):
                dwell_weight = 0.1
            if (int(flight_weight) == 0):
                flight_weight = 0.1
            score2[index] = (dwell_weight * dwellScore[index]) + (flight_weight * flightScore[index])

        if (self.args.debug):
            print ("keyAffinity: " + str(keyAffinity) + "\n")
            print ("user list: " + str(Users) + "\n")
            print ("dwell value hits: " + str(checkDwellValue) + "\n")
            print ("flight value hits: " + str(checkFlightValue) + "\n")
            print ("dwell score: " + str(dwellScore) + "\n")
            print ("flight score: " + str(flightScore) + "\n")
            print ("final candidates scores\n" + str(collections.OrderedDict(sorted(score2.items()))) + "\n")
 
        if (score2.keys()):
            identity_order = sorted(score2.items() , key=operator.itemgetter(1))
        else:
            print ("I don't know you. Who are you?")
            exit()

        identity_order = self.keyAffinityMatch(keyAffinity, Users, identity_order, keyAffinityOfUsers)

        for name_index in range(0,len(identity_order)):
            print ("Rank " + str(name_index) + ": " + str(identity_order[name_index]))


    def keyAffinityMatch(self, keyAffinity, Users=[], identityOrder=[], keyAffinityOfUsers=[]):
        if (self.args.debug):
            print ("keyAffinityMatch")
        
        identityOrder_Affinity = []
        identity_rank = []
        not_found = []
        found = 0

        for index in range(0,len(Users)):
            if (int(keyAffinity) == int(keyAffinityOfUsers[index])):
                identityOrder_Affinity.append(Users[index][0])

        for name in identityOrder:
            name_index = int(name[0][1:])
            for name_affinity in identityOrder_Affinity:
                if (str(name_affinity) == str(Users[name_index][0])):
                    identity_rank.append(Users[name_index][0])
                    found = 1
            if (found == 0):
                not_found.append(Users[name_index][0])
            found = 0

        for name in not_found:
            identity_rank.append(name)

        return identity_rank 
        
    # This function is similar to findParams except that it stores
    # the ID values and the user name in a .csv file and exits
    # This function is used only for training for the script and
    # is unused while testing
    def storeParams(self, user, keyAffinity, dwell = [] , flight = []):
        if (self.args.debug):
            print ("storeParams") 

        if (len(dwell) != self.dwellLength or len(flight) != self.flightLength):
            print ("Weird... I couldn't extract the information I need. Please retry.")
            exit()

        with open('dwellFlightkeyboard/flight_Time_' + user + '.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(flight)

        with open('dwellFlightkeyboard/dwell_Time_' + user + '.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(dwell)
  
        with open('Users.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow([user])

        with open('keyAffinity_keyboard.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow([keyAffinity])

        print ("X, Y values stored for %s"  % user)
    
    # This function finds the user associated with the
    # matched ID values
    def findUser(self, keyAffinity, X,Y):
        if (self.args.debug):
            print ("findUser")

        for key,value in self.Users_ID.items():
            if(abs(value - (X+Y)) < 0.5):
                if (int(keyAffinity) == int(self.Users_keyAffinity[key])):
                    return key
                else:
                    return str(key) + " detected but something is not correct. Allowing to pass but this will be logged."

    def getch(self):
        if (self.args.debug):
            print ("getch")
    
        time_elapsed = pygame.time.get_ticks()
        time_down = 0.0
        time_down_1 = 0.0
        input_str = '' 
        flight_elapsed = []
        dwell_elapsed = [] 
        keyAffinity = 0
        screen = pygame.display.set_mode((480, 720))
        comic_sans_font = pygame.font.SysFont("comicsansms", 24)
 
        text = comic_sans_font.render('Enter password: ', True, (0, 0, 0))
        screen.fill((255,255,255))
        screen.blit(text, (10,10))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (input_str, flight_elapsed, dwell_elapsed)
                elif event.type == pygame.KEYDOWN:
                    time_down = pygame.time.get_ticks()
                    if (event.key == pygame.K_LSHIFT):
                        keyAffinity = 8
                    if (event.key == pygame.K_RSHIFT):
                        keyAffinity = 2
                    if (event.key == pygame.K_CAPSLOCK):
                        keyAffinity = 5
                    if (event.unicode == '\r'):
                        return (input_str, keyAffinity, flight_elapsed, dwell_elapsed)
                    if (len(input_str)):
                        flight_elapsed.append((time_down - time_down_1)/1000)
                    input_str += event.unicode
                elif event.type == pygame.KEYUP:
                    dwell_elapsed.append((pygame.time.get_ticks() - time_down)/1000)
                    time_down_1 = pygame.time.get_ticks()

            if (self.args.debug):
                print (dwell_elapsed)

            text = comic_sans_font.render(input_str, True, (0, 0, 0))
            screen.blit(text, (140, 10))

            pygame.display.update()

    def checkPassword(self, inPassword):
        if (self.args.debug):
            print ("checkPassword")

        if (self.password == inPassword):
            return 1
        else:
            return 0

    def captureKey(self, action, user):
        if (self.args.debug):
            print ("captureKey")

        (self.inputstr, keyAffinity, self.flight_elapsed, self.dwell_elapsed) = self.getch();
  
        # Debug
        #print (self.inputstr) 
        #print (self.flight_elapsed)
        #print (self.dwell_elapsed)
        #print ("Shift used: " + str(shift))

        passCheck = self.checkPassword(self.inputstr)
        if(not passCheck):
            print ("Incorrect password. Exiting...")
            exit()

        self.flightDwellTest(action, user, keyAffinity)
    
    def flightDwellTest(self, action, user, keyAffinity):
        if (self.args.debug):
            print ("flightDwellTest") 
    
        self.user = user
        # These blocks control whether the script is in training mode or test mode
        # depending on the arguments passed to the script
        if (action == 'train'):
            username = user 
            self.storeParams(username, keyAffinity, self.dwell_elapsed , self.flight_elapsed)
    
        if (action == 'test'):
            self.findMatch(action, keyAffinity, self.dwell_elapsed , self.flight_elapsed)
    
    def formatInput(self, x , y):
        if (self.args.debug):
            print ("formatInput")

        x = x.split(',')
        y = y.split(',')
        for i in range(len(x)):
            x[i] = float(x[i])
            y[i] = float(y[i])
        return (x,y)
   
    def main(self):
        #parser = argparse.ArgumentParser(description='Keystroke Dynamics for keyboard')
        #parser.add_argument('-action', metavar = '[test|train]', type = str, args = 1, required = True, help = 'Action to take')
        #parser.add_argument('-user', type = str, help = 'Training of script => Username of the person')
        #parser.add_argument('-debug', action = 'store_true')			
        #args = parser.parse_args()

        if (self.args.debug):
            print ("main")

        if (self.args.b_testing):
            keyAffinity = 2
            action = 'test'
            dwell = [] 
            flight = []
 
            for filename in os.listdir("benchmark/"):
                count = 0

                if re.search('dwell_Time', str(filename)):
                    file_index = re.findall('\d+', str(filename))
                    with open('benchmark/' + str(filename), 'rt') as src:
                        reader = csv.reader(src)
                        for data in reader:
                            dwell.append(data)
                    flight_filename = 'flight_Time_s' + file_index[0] + '.csv'
                    with open('benchmark/' + str(flight_filename), 'rt') as src:
                        reader = csv.reader(src)
                        for data in reader:
                            flight.append(data)

                while (count < 5 and len(dwell) != 0 and len(flight) != 0):
                    print ('Subject being tested: ' + str(filename))
                    index = randint(0,399)
                    if (dwell[index] != 0 and
                        flight[index] != 0):
                        self.dwell_elapsed = dwell[index]
                        self.flight_elapsed = flight[index]    
                    else:
                        continue
                    keyAffinity = 1
                    self.findMatch(action, keyAffinity, self.dwell_elapsed , self.flight_elapsed)
                    count = count + 1

                dwell = []
                flight = []

            exit(0)

        self.captureKey(self.args.action[0],self.args.user)
        
myObject = KeyDynamics()
myObject.main()
