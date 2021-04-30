import math
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle


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


# Page size in bytes
PAGE_SIZE = 4096
MASK_SIZE = math.log(PAGE_SIZE, 2)
MASK = "0xfffffffff000"

def get_mem_reuse(filename):

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

    reuse_distances = get_page_reuse_distances(pages)

    return pages, reuse_distances