import csv, math, os, re, argparse

password = '.zoroBen1'
dwell_length = len(password) + 1
flight_length = len(password)

parser = argparse.ArgumentParser(description='Find mean and standard deviation for all timings file present in benchmark directory')
parser.add_argument('-debug', action='store_true')
args = parser.parse_args()

def openFile(filename, file_path):
    if (args.debug):
        print ("openDwellFile")
    with open (file_path + '/../benchmark/' + filename , 'rt') as f:
        reader = csv.reader(f)
        dwellTime = list(reader)
    return dwellTime

def formatArray(arr=[]):
    if (args.debug):
        print ("formatArray")
    formattedArray = []
    for subarr in arr:
        for value in subarr:
            formattedArray.append(value)
    return formattedArray

def writeToFile(typeIs, arrMean=[], arrDeviation=[]):
    if (args.debug):
        print ("writeToFile")
    file_path = str(os.getcwd())
    if (typeIs == 'dwell'):
        with open(file_path + '/../benchmark/dwellMean.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(arrMean)
        with open(file_path + '/../benchmark/dwellDeviation.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(arrDeviation)
    else:
        with open(file_path + '/../benchmark/flightMean.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(arrMean)
        with open(file_path + '/../benchmark/flightDeviation.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(arrDeviation)

def findEstimates(allowedVariation, fileValues=[]):
    if (args.debug):
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
    return estimate

def findDeviations(mean, buildArr):
    length = len(buildArr)
    sumValues = 0.0
    for value in buildArr:
        sumValues += math.pow((float(value) - mean) , 2)

    return math.sqrt(float(1/length) * sumValues)

def findMode(index, typeIs, arr=[]):
    global dwell_length, flight_length

    i = index
    sumValues = 0.0
    allowedVariation = 0.01
    buildArr = []
    
    while(1):
        buildArr.append(arr[i])
        if (typeIs == 'dwell'):
            i = i + dwell_length
        else: 
            i = i + flight_length
        if (i >= len(arr)):
            break

    estimate = findEstimates(allowedVariation, buildArr)
    deviation = findDeviations(estimate, buildArr)
    return (estimate, deviation)

def DwellFile(files):
    if (args.debug):
        print ('Finding dwell files')
    dwell_files = []
    for f in files:
        if (re.search('dwell_Time', str(f))):
            dwell_files.append(f)
    return dwell_files

def FlightFile(files):
    if (args.debug):
        print ('Finding flight files')
    flight_files = []
    for f in files:
        if (re.search('flight_Time', str(f))):
            flight_files.append(f)
    return flight_files

def main():
    global password
    if (args.debug):
        print ("main")
    passLen = len(password)
    buildMeanDwellArr = []
    buildDeviationDwellArr = []
    buildMeanFlightArr = []
    buildDeviationFlightArr = []

    #files = [f for f in os.listdir('.') if os.path.isfile(f)]
    file_path = os.getcwd()
    files = os.listdir(file_path + '/../benchmark')
    dwell_files = DwellFile(files)
    flight_files = FlightFile(files)

    for read_file in dwell_files:
        dwellTime = openFile(read_file, file_path)
        dwellTime = formatArray(dwellTime)
        for index in range(0, passLen+1):
            (mean, deviation) = findMode(index, 'dwell', dwellTime)
            buildMeanDwellArr.append(mean)
            buildDeviationDwellArr.append(deviation)
        writeToFile('dwell', buildMeanDwellArr, buildDeviationDwellArr)
        buildMeanDwellArr = []
        buildDeviationDwellArr = []

    for read_file in flight_files:
        flightTime = openFile(read_file, file_path)
        flightTime = formatArray(flightTime)
        for index in range(0, passLen):
            (mean, deviation) = findMode(index, 'flight', flightTime)
            buildMeanFlightArr.append(mean) 
            buildDeviationFlightArr.append(deviation)
        writeToFile('flight', buildMeanFlightArr, buildDeviationFlightArr) 
        buildMeanFlightArr = []
        buildDeviationFlightArr = []

main()
