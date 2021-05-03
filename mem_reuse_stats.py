import math
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle
from mem_reuse_gen import get_mem_reuse

parser = argparse.ArgumentParser(description='A tutorial of argparse!')
parser.add_argument("--load", type=bool, default=False)
parser.add_argument("--target", type=str)
args = parser.parse_args()

def save_list(data, filename):
    with open(filename, "wb") as fp:
        pickle.dump(data, fp)

def load_list(filename):
    with open(filename, "rb") as fp:   # Unpickling
       return pickle.load(fp)

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

def graph_reuse_distances(filename, cdfs):
    n_groups =  len( range(0, 20))
    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8
    rects = plt.bar(index, cdfs, bar_width)

    plt.xlabel('Reuse Distances(log scale)')
    plt.ylabel('CDF')
    plt.title('Reuse Distances for Memory Accesses: ' + filename)
    plt.xticks(index, range(0, 19))

    plt.tight_layout()
    plt.savefig('graphs/' + str(filename) + ".png")    
    plt.close()


def main():
    # Page size in bytes
    PAGE_SIZE = 4096
    MASK_SIZE = math.log(PAGE_SIZE, 2)
    MASK = "0xfffffffff000"
    filenames = []
    all_avg_reuse_distances = []
    all_reuse_percentages = []
    all_cdfs = []
    pages = []
    page_reuse_percentages = []
    if not args.load:
        if not args.target:
            for filename in os.listdir('memtraces'):
                
                avg_reuse_distance, page_reuse_percentage, cdfs = get_mem_reuse(os.path.join("memtraces", filename))
                save_list((avg_reuse_distance, page_reuse_percentage, cdfs), "stats/" + filename)

                all_avg_reuse_distances.append(avg_reuse_distance)
                all_reuse_percentages.append(page_reuse_percentage)
                all_cdfs.append(cdfs)
                filenames.append(filename)
        else:
            filename = args.target
            avg_reuse_distance, page_reuse_percentage, cdfs = get_mem_reuse(filename)
            save_list((avg_reuse_distance, page_reuse_percentage, cdfs), "stats/" + os.path.basename(filename))

            all_avg_reuse_distances.append(avg_reuse_distance)
            all_reuse_percentages.append(page_reuse_percentage)
            all_cdfs.append(cdfs)
            filenames.append(filename)

    else:
        for filename in os.listdir('Stats'):
            data = load_list("Stats/" + filename)
            all_avg_reuse_distances.append(data[0])
            all_reuse_percentages.append(data[1])
            all_cdfs.append(data[2])
            filenames.append(filename[0:len(filename)-3])
            
    create_reuse_percent_plot(filenames, all_reuse_percentages)
    create_avg_reuse_distance_plot(filenames, all_avg_reuse_distances)

    for cdfs in all_cdfs:
        graph_reuse_distances(filename, cdfs)
        
if __name__ == "__main__":
    main()
