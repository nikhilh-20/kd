import csv, re, os

basedir = os.getcwd() + '/../benchmark/'
read_file = basedir + 'benchmark_dataset.csv'
write_dwell_file = basedir + 'dwell_Time_'
write_flight_file = basedir + 'flight_Time_'
write_users_file = basedir + 'users_Converged.csv'
write_key_file = basedir + 'key_keyboard_values.csv'

subject = 0
data_to_write = ''

def shouldISkip(data):
    count = 0
    dwell_data_to_write = []
    flight_data_to_write = []
    key = 1
    subject = ''
  
    for values in data:
        if (re.search('s0', str(data[0]))):
            subject = data[0]
            if (count == 0 or count == 1 or count == 2 or count == 5 or
                count == 8 or count == 11 or count == 14 or count == 17 or
                count == 20 or count == 23 or count == 26 or count == 29 or 
                count == 31 or count == 32 or count == 33):
                count = count + 1
                continue
            elif (count == 3 or count == 6 or count == 9 or count == 12 or
                  count == 15 or count == 18 or count == 21 or count == 24 or
                  count == 27 or count == 30):
                dwell_data_to_write.append(values)
                count = count + 1
            else:
                flight_data_to_write.append(values)
                count = count + 1
         
    return (dwell_data_to_write, flight_data_to_write, key, subject)

with open(read_file, 'rt') as src:
    reader = csv.reader(src)

    users = []
    keys = []

    for data in reader:
        count = 0

        if(data[0] == 'subject'):
            continue 

        (dwell_data_to_write, flight_data_to_write, key_value, subject) = shouldISkip(data)
        write_dwell_file = write_dwell_file + str(subject) + '.csv'
        write_flight_file = write_flight_file + str(subject) + '.csv'

        writer = csv.writer(open(write_dwell_file, 'a'))
        writer.writerow(dwell_data_to_write)
        writer = csv.writer(open(write_flight_file, 'a'))
        writer.writerow(flight_data_to_write)

        write_dwell_file = basedir + 'dwell_Time_'
        write_flight_file = basedir + 'flight_Time_'
  
        if subject not in users:
            writer = csv.writer(open(write_users_file, 'a'))
            writer.writerow([subject])
            users.append(subject)
            writer = csv.writer(open(write_key_file, 'a'))
            writer.writerow([key_value])
