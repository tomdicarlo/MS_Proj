import math
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle
from mem_reuse_gen import get_mem_reuse

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

def avg_reuse_distances(reuse_distances):
    Sum = 0
    count = 0
    for page in reuse_distances:
        distances = reuse_distances[page]
        Sum += sum(distances)
        count += len(distances)
    if(count != 0):
        return Sum/count
    return 0

def save_list(data, filename):
    with open(filename, "wb") as fp:
        pickle.dump(data, fp)

def load_list(filename):
    with open(filename, "rb") as fp:   # Unpickling
       return pickle.load(fp)

def get_data_reuse_percent(pages):
    total_count = 0 
    total_reused = 0
    for page in pages:
        if pages[page] > 1:
            total_reused += 1
        total_count += 1

    return total_reused/total_count     


def create_reuse_percent_plot(filenames, reuse_percentages):
    n_groups =  len(filenames)
    # create plot
    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8
    rects = plt.bar(index, reuse_percentages, bar_width)

    plt.xlabel('File')
    plt.ylabel('Percentage of Data Reuses')
    plt.title('Data Reuse Percentages for Spec2017 Test Suites')
    plt.xticks(index, tuple(filenames))

    plt.tight_layout()
    plt.savefig('graphs/reuse_percent')    
    plt.show()

def create_avg_reuse_distance_plot(filenames, all_avg_reuse_distances):
    n_groups =  len(filenames)
    # create plot
    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    ax=plt.gca()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8
    rects = plt.bar(index, all_avg_reuse_distances, bar_width)

    plt.xlabel('File')
    plt.ylabel('Avg Distances')
    plt.title('Average Memory Reuse Distance for Spec2017 Test Suites')
    plt.xticks(index, tuple(filenames))

    plt.tight_layout()
    plt.savefig('graphs/avg_reuse')    
    plt.show()


def graph_reuse_distances(filename, distances):
    cdfs = []
    for i in range(1, 19):
        total = 0
        count_below = 0
        boundary = 2**i
        for page in distances:
            for distance in distances[page]:
                if distance < boundary:
                    count_below += 1
                total += 1
        cdfs.append(count_below/total)
    
    n_groups =  len( range(1, 19))
    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8
    rects = plt.bar(index, cdfs, bar_width)

    plt.xlabel('Reuse Distances(log scale)')
    plt.ylabel('CDF')
    plt.title('Reuse Distances for Memory Accesses: ' + filename)
    plt.xticks(index, range(1, 19))

    plt.tight_layout()
    plt.savefig('graphs/' + str(filename) + ".png")    



# Page size in bytes
PAGE_SIZE = 4096
MASK_SIZE = math.log(PAGE_SIZE, 2)
MASK = "0xfffffffff000"
filenames = []
all_reuse_distances = []
pages = []
page_reuse_percentages = []
if not args.load:
    for filename in os.listdir('memtraces'):
        
        pages, reuse_distances = get_mem_reuse(filename)
        save_list(reuse_distances, "reuse_distances/" + filename)
        save_list(pages, "pages/" + filename)

        page_counts, page_percentages = get_page_stats(pages)
        print_page_stats(page_counts, page_percentages)

        print(reuse_distances)

        all_reuse_distances.append(reuse_distances)
        pages.append(pages)
        filenames.append(filenames)
        
else:
    for filename in os.listdir('reuse_distances'):
        reuse_distance = load_list("reuse_distances/" + filename)
        page = load_list("pages/" + filename)
        all_reuse_distances.append(reuse_distance)
        filenames.append(filename[0:len(filename)-3]) 
        pages.append(page)
        

all_avg_reuse_distances = []

for distance in all_reuse_distances:
    avg = avg_reuse_distances(distance)
    all_avg_reuse_distances.append(avg)

for page in pages:
    page_counts, page_percentages = get_page_stats(page)
    page_reuse_percent = get_data_reuse_percent(page_counts)
    page_reuse_percentages.append(page_reuse_percent)

create_reuse_percent_plot(filenames, page_reuse_percentages)
create_avg_reuse_distance_plot(filenames, all_avg_reuse_distances)

for i in range(0,len(all_reuse_distances)):
    filename = filenames[i]
    distances = all_reuse_distances[i]
    graph_reuse_distances(filename, distances)
    