from __future__ import division

import pygame, csv, operator
from pygame.locals import *

from key_dy_init import key_dy_init

key_dy_obj = key_dy_init()

def keyAffinityMatch(keyAffinity, Users=[], identityOrder=[], keyAffinityOfUsers=[]):
    """

    """

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

def findUserMatch(keyAffinity, Users=[], keyAffinityOfUsers=[], checkDwellValue=[], checkFlightValue=[], dwellScore={}, flightScore={}):
    """

    """

    score = {}
    score2 = {}
    minKey = 'k0'
    minScore = {minKey : 100}
    sumReference = []
    found = 0
    finalScore = {}

    for index in dwellScore:
        dwell_weight = key_dy_obj.dwellLength - checkDwellValue[int(index[1:])]
        flight_weight = key_dy_obj.flightLength - checkFlightValue[int(index[1:])]
        if (int(dwell_weight) == 0):
            dwell_weight = 0.1
        if (int(flight_weight) == 0):
            flight_weight = 0.1
        score2[index] = (dwell_weight * dwellScore[index]) + (flight_weight * flightScore[index])
    if (score2.keys()):
        identity_order = sorted(score2.items() , key=operator.itemgetter(1))
    else:
        print ("I don't know you. Who are you?")
        exit()

    identity_order = keyAffinityMatch(keyAffinity, Users, identity_order, keyAffinityOfUsers)

    for name_index in range(0,len(identity_order)):
        print ("Rank " + str(name_index) + ": " + str(identity_order[name_index]))

def findHits(inputType, templateMean=[], templateDeviation=[], featureInput=[]):
    """
    Finds character-by-character matches

    Args:
        inputType        : dwell | flight
        templateMean     : The inputType timing sample list of templates
        templateDeviation: The inputType standard deviation list of templates
        featureInput     : The user input timing sample list
    Raises:
        None
    Returns:
        checkValue:
        scoreDict :
    """

    sumValues = 0.0
    scoreDict = {}
    checkValue = [0] * len(templateMean)

    for indexOuter in range(0, len(templateMean)):
        checkValue[indexOuter] = 0
        for indexInner in range(0, len(templateMean[indexOuter])):
            diff = abs(float(featureInput[indexInner]) - float(templateMean[indexOuter][indexInner]))
            if (str(inputType) == 'dwell'):
                if (diff <= 1.25 * float(templateDeviation[indexOuter][indexInner])):
                    checkValue[indexOuter] += 1
            elif (str(inputType) == 'flight'):
                if (diff <= float(templateDeviation[indexOuter][indexInner])):
                    checkValue[indexOuter] += 1
            else:
                print ("Couldn't recognize type of input")
                exit()
            sumValues += diff
        scoreDict['k' + str(indexOuter)] = (sumValues)
        sumValues = 0.0

    return (checkValue, scoreDict)

def findMatch(keyAffinity, dwell=[], flight=[]):
    """
    Finds matches character-by-character and then calculates a list of users indecreasing order of probability

    Args:
        keyAffinity: flag which differentiates between usage of caps-lock and shift keys
        dwell      : dwell-time samples list
        flight     : flight-time samples list
    Raises:
        Exception - sometimes when two keys are pressed at the same time, I'm not able to collect accurate timing data
    Returns:
        None
    """

    if (len(dwell) != key_dy_obj.dwellLength or len(flight) != key_dy_obj.flightLength):
        raise Exception ("Weird... I couldn't extract the information I need. Please retry.")

    if (key_dy_obj.args.b_testing):
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
        with open ('../dwellFlightKeyboard/dwellMean.csv' , 'rt') as f:
            reader = csv.reader(f)
            dwellMean = list(reader)
        with open ('../dwellFlightKeyboard/dwellDeviation.csv' , 'rt') as f:
            reader = csv.reader(f)
            dwellDeviation = list(reader)
        with open ('../dwellFlightKeyboard/flightMean.csv' , 'rt') as f:
            reader = csv.reader(f)
            flightMean = list(reader)
        with open ('../dwellFlightKeyboard/flightDeviation.csv' , 'rt') as f:
            reader = csv.reader(f)
            flightDeviation = list(reader)
        with open ('../dwellFlightKeyboard/users_Converged.csv' , 'rt') as f:
            reader = csv.reader(f)
            Users = list(reader)
        with open ('../dwellFlightKeyboard/key_keyboard_values.csv' , 'rt') as f:
            reader = csv.reader(f)
            keyAffinity_ofUser = list(reader)

    # Correcting the format of the array
    for index in range(0,len(keyAffinity_ofUser)):
        keyAffinity_ofUser[index] = keyAffinity_ofUser[index][0]

    (checkDwellValue, scoreDwellDict) = findHits('dwell', dwellMean, dwellDeviation, dwell)
    (checkFlightValue, scoreFlightDict) = findHits('flight', flightMean, flightDeviation, flight)
    findUserMatch(keyAffinity, Users, keyAffinity_ofUser, checkDwellValue, checkFlightValue, scoreDwellDict, scoreFlightDict)

def storeParams(user, keyAffinity, dwell = [] , flight = []):
    """
    Stores the user's timing samples as well as their key-affinity flag value

    Args:
        user       : name of the user who's training the system (to be used only while training)
        keyAffinity: flag which differentiates between usage of caps-lock and shift keys
        dwell      : dwell-time samples list
        flight     : flight-time samples list
    Raises:
        Exception - sometimes when two keys are pressed at the same time, I'm not able to collect accurate timing data
    Returns:
        None
    """

    if (len(dwell) != key_dy_obj.dwellLength or len(flight) != key_dy_obj.flightLength):
        raise Exception ("Weird... I couldn't extract the information I need. Please retry.")

    with open('../dwellFlightKeyboard/flight_Time_' + user + '.csv' , 'a') as f:
        writer = csv.writer(f)
        writer.writerow(flight)

    with open('../dwellFlightKeyboard/dwell_Time_' + user + '.csv' , 'a') as f:
        writer = csv.writer(f)
        writer.writerow(dwell)

    with open('../Users.csv' , 'a') as f:
        writer = csv.writer(f)
        writer.writerow([user])

    with open('../keyAffinity_Keyboard.csv' , 'a') as f:
        writer = csv.writer(f)
        writer.writerow([keyAffinity])

    print ("X, Y values stored for %s"  % user)

def checkPassword(inPassword):
    """
    Verify the correctness of the user-input password

    Args:
        inPassword: user-input password
    Raises:
        Exception - If the password is incorrect
    Returns:
        None
    """

    if (key_dy_obj.password != inPassword):
        raise Exception ('Incorrect password!')

def getch():
    """
    Opens a pygame window where the user types the password. The timing samples are determined at the same time

    Args:
    Raises:
        None
    Returns:
        Tuple - (input-string-password, key-affinity-flag-value, flight-timing-sample-list, dwell-timing-sample-list)
    """

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

        text = comic_sans_font.render(input_str, True, (0, 0, 0))
        screen.blit(text, (140, 10))

        pygame.display.update()

def flightDwellTest(action, user, keyAffinity):
    """
    Branches the code flow depending on the action

    Args:
        action     : test | train
        user       : the name of the user who's training the system (to be used only while training)
        keyAffinity: the flag which differentiates between usage of caps-lock and shift keys
    Raises:
    Returns:
        None
    """
    key_dy_obj.user = user
    # These blocks control whether the script is in training mode or test mode
    # depending on the arguments passed to the script
    if (action == 'train'):
        username = user
        storeParams(username, keyAffinity, key_dy_obj.dwell_elapsed , key_dy_obj.flight_elapsed)
    else:
        findMatch(keyAffinity, key_dy_obj.dwell_elapsed , key_dy_obj.flight_elapsed)

def captureKey(action, user):
    """
    Captures user input, verifies correctness of the password

    Args:
        action: test | train
        user  : the name of the user who's training the system (to be used only while training)
    Raises:
        Exception - If incorrect 'action' value was provided
    Returns:
        None
    """

    if action != 'train' and action != 'test':
        raise Exception ('Incorrect \'action\' value. Exiting...')

    (key_dy_obj.inputstr, keyAffinity, key_dy_obj.flight_elapsed, key_dy_obj.dwell_elapsed) = getch();

    checkPassword(key_dy_obj.inputstr)
    flightDwellTest(action, user, keyAffinity)

def main():
    """
    main function - starting point to this script

    Args:
    Raises:
    Returns:
        None
    """

    if (key_dy_obj.args.b_testing):
        keyAffinity = 2
        action = 'test'
        dwell = []
        flight = []

        for filename in os.listdir("../benchmark/"):
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
                    key_dy_obj.dwell_elapsed = dwell[index]
                    key_dy_obj.flight_elapsed = flight[index]
                else:
                    continue
                keyAffinity = 1
                key_dy_obj.findMatch(action, keyAffinity, key_dy_obj.dwell_elapsed , key_dy_obj.flight_elapsed)
                count = count + 1
            dwell = []
            flight = []
            print ("Completed bench mark testing. Exiting...")
            exit(0)

    captureKey(key_dy_obj.args.action[0], key_dy_obj.args.user)

main()
