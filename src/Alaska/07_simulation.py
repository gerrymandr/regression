#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 16:59:43 2018

@author: samirkhan
"""
import csv
import numpy as np
from tqdm import tqdm

#Define matching of (1,2), (3,4) which corresponds to actual matching
true_matching = [(str(i), str(i+1)) for i in range(1, 41, 2)]


#Read in csv with vote counts by district, store as dictionary
def load_data(filename):
    data = {}
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            data[row[0]] = np.array([float(row[1]), float(row[2])])

    return data

#Helper function that takes list of districts and matches in blocks of two
def make_matching(l):
    return [l[i:i+2] for i in range(0, len(l)-1, 2)]

#Get parameters of poisson distributions for each party for each district
def get_params(matching, data):
    dem_ls = []
    rep_ls = []

    for match in matching:
        m_dem_votes = data[match[0]][0]+data[match[1]][0]
        m_rep_votes = data[match[0]][1]+data[match[1]][1]

        dem_ls.append(m_dem_votes)
        rep_ls.append(m_rep_votes)


    return dem_ls, rep_ls

#Simulate a single set of races for a matching
def simulate(matching, data):
    dem_ls, rep_ls = get_params(matching, data)
    seats = 0
    for (dem_l, rep_l) in zip(dem_ls, rep_ls):
        dem_votes = np.random.poisson(dem_l)
        rep_votes = np.random.poisson(rep_l)
        if dem_votes > rep_votes:
            seats +=1
    return seats


#Loop over all matchings, simulating 100 sets of races for each
def check_all_matchings(data):
    all_seats = []

    with open("AKallpairings.csv") as f:
        reader = csv.reader(f)
        for row in tqdm(reader):
            match_seats = []

            matching = make_matching(row)
            for j in range(100):
                seats = simulate(matching, data)
                match_seats.append(seats)

            all_seats+=match_seats


    return all_seats
