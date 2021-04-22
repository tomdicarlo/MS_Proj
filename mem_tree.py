import math
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle

parser = argparse.ArgumentParser(description='A tutorial of argparse!')
parser.add_argument("--load", type=bool, default=False)
args = parser.parse_args()

def get_page_stats(pages):
    total_count = 0;
    page_counts = {}
    for page in pages:
        if page in page_counts:
            page_counts[page] += 1
        else:
            page_counts[page] = 1
        total_count += 1
        
    page_counts = {key: value for key, value in reversed(sorted(page_counts.items(), key=lambda item:item[1]))}
    page_percentages = {}

    for page in page_counts:
        page_percentages[page] = page_counts[page]/total_count

    return page_counts, page_percentages

def print_page_stats(page_counts, page_percentages):
    print("Total number of pages: " + str(len(page_counts)))
    print("Number of Accesses:")
    for page in page_counts:
        print("Page " + page + ": " + str(page_counts[page]))

    print("Percentage of Accesses:")
    for page in page_percentages:
        print("Page " + page + ": " + str(page_percentages[page]))

def get_page_reuse_distances(pages):
    page_accesses = {}
    reuse_distances = {}
    for page in pages:
        if not page in page_accesses:
            page_accesses[page] = []
        else:
            reuse_distance = len(page_accesses[page])
            if not page in reuse_distances:
                reuse_distances[page] = []

            reuse_distances[page].append(reuse_distance)
            page_accesses[page] = []

        for access_record in page_accesses:
            if access_record != page and page not in page_accesses[access_record]:
                page_accesses[access_record].append(page)

    return reuse_distances

def avg_reuse_distances(reuse_distances):
    Sum = 0
    count = 0
    for page in reuse_distances:
        distances = reuse_distances[page]
        Sum += sum(distances)
        count += len(distances)
    return Sum/count

def save_list(data, filename):
    with open(filename, "wb") as fp:
        pickle.dump(data, fp)

def load_list(filename):
    with open(filename, "rb") as fp:   # Unpickling
       return pickle.load(fp)


# Page size in bytes
PAGE_SIZE = 4096
MASK_SIZE = math.log(PAGE_SIZE, 2)
MASK = "0xfffffffff000"
filenames = []
all_reuse_distances = []

if not args.load:
    for filename in os.listdir('memtraces'):
        print(filename)
        filenames.append(filename)
        f = open(os.path.join("memtraces", filename), "r")
        data = f.read().split("\n")

        instructions = []
        access_types = []
        addresses = []
        pages = []

        for row in data:
            if(row != "#eof" and row!=""):
                
                instance = row.split()
                if(len(instance) != 3):
                    print(row)
                else:
                    try:
                        page = int(instance[2], 16) & int(MASK, 16)

                        instructions.append(instance[0][:-1])
                        access_types.append(instance[1])
                        addresses.append(instance[2])
                        pages.append(hex(page))
                    except:
                        print(row)

        page_counts, page_percentages = get_page_stats(pages)
        print_page_stats(page_counts, page_percentages)

        reuse_distances = get_page_reuse_distances(pages)

        print(reuse_distances)

        

        all_reuse_distances.append(reuse_distances)
        
    save_list(all_reuse_distances, "outputs/reuse_distances.txt")
    save_list(filenames, "outputs/filenames.txt")
else:
    all_reuse_distances = load_list("outputs/reuse_distances.txt")
    
    filenames = load_list("outputs/filenames.txt")
    
final_stats = []

for distance in all_reuse_distances:
    avg = avg_reuse_distances(distance)
    final_stats.append(avg)
    print("Average Reuse Distance:")
    print(avg)

n_groups =  len(filenames)
# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.35
opacity = 0.8
print(final_stats)
rects = plt.bar(index, final_stats, bar_width, alpha=opacity, color='b', label='Avg Reuse Distances')

plt.xlabel('File')
plt.ylabel('Avg Distances')
plt.title('Average Memory Reuse Distance for Spec2017 Test Suites')
plt.xticks(index, (filenames[0], filenames[1]))
plt.legend()

plt.tight_layout()
plt.show()