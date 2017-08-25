import re, os, argparse

subject_ranks = {}
ranks_percentages = {}
total_samples = 0

parser = argparse.ArgumentParser(description='Calculate rank-k statistics')
parser.add_argument('-file', metavar='filename', type=str, nargs=1, help='Filename which has rank related information')
args = parser.parse_args()

basedir = os.getcwd()
filename = str(basedir) + '/../' + str(args.file[0])
write_file = str(basedir) + '/../rank-k.txt'

with open(filename, 'rt') as src:
    for rank in src:
        if (re.search('Subject being tested', str(rank))):
            subject_num = re.findall('\d+', str(rank))
            for rank_line in src:
                rank_line.strip()
                if (re.search(str(subject_num[0]), str(rank_line))):
                    rank_num = re.findall('\d+', str(rank_line))
                    if (rank_num[0] not in subject_ranks):
                        subject_ranks[rank_num[0]] = 1
                    else:
                        subject_ranks[rank_num[0]] += 1
                    break

for keys in subject_ranks:
    total_samples += subject_ranks[keys]    
    if int(keys) not in ranks_percentages:
        ranks_percentages[keys] = 0

for keys in subject_ranks:
    if str(keys) not in subject_ranks:
        continue
    for rank in range(0, int(keys)):
        if str(rank) in subject_ranks:
            ranks_percentages[str(keys)] += subject_ranks[str(rank)]

for keys in ranks_percentages:
    ranks_percentages[keys] = 100 * (ranks_percentages[keys] / total_samples)

with open(write_file, 'a') as dst:
    dst.write('%s%s %s' %('Rank-k\n' , str(subject_ranks), '\n\n')) 
    dst.write('%s%s %s' %('Total samples:\n', str(total_samples), '\n\n'))
    dst.write('%s%s %s' %('Rank percentages:\n', str(ranks_percentages), '\n\n'))
    dst.write('%s%s' %('Minimum achievable efficiency:\n' , str(min(ranks_percentages, key=ranks_percentages.get))))
