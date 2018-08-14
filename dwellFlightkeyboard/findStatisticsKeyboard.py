import csv, math

password = '.zoroBen1'
dwell_length = len(password) + 1
flight_length = len(password)

def openFile(filename):
    print ("openDwellFile")
    with open (filename , 'rt') as f:
        reader = csv.reader(f)
        dwellTime = list(reader)
    return dwellTime

def formatArray(arr=[]):
    print ("formatArray")
    formattedArray = []
    for subarr in arr:
        for value in subarr:
            formattedArray.append(value)
    return formattedArray

def writeToFile(typeIs, arrMean=[], arrDeviation=[]):
    print ("writeToFile")
    if (typeIs == 'dwell'):
        with open('dwellMean.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(arrMean)
        with open('dwellDeviation.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(arrDeviation)
    else:
        with open('flightMean.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(arrMean)
        with open('flightDeviation.csv' , 'a') as f:
            writer = csv.writer(f)
            writer.writerow(arrDeviation)

def findEstimates(allowedVariation, fileValues=[]):
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

def main():
    global password

    print ("main")
    passLen = len(password)
    buildMeanDwellArr = []
    buildDeviationDwellArr = []
    buildMeanFlightArr = []
    buildDeviationFlightArr = []

    dwellTime = openFile('dwell_Time_anuj.csv')
    dwellTime = formatArray(dwellTime)
    for index in range(0, passLen+1):
        (mean, deviation) = findMode(index, 'dwell', dwellTime)
        buildMeanDwellArr.append(mean)
        buildDeviationDwellArr.append(deviation)

    flightTime = openFile('flight_Time_anuj.csv')
    flightTime = formatArray(flightTime)
    for index in range(0, passLen):
        (mean, deviation) = findMode(index, 'flight', flightTime)
        buildMeanFlightArr.append(mean) 
        buildDeviationFlightArr.append(deviation)

    writeToFile('dwell', buildMeanDwellArr, buildDeviationDwellArr)
    writeToFile('flight', buildMeanFlightArr, buildDeviationFlightArr) 
    
main()
