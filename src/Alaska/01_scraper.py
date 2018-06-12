#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 14:19:47 2018

@author: samirkhan
"""

from tqdm import tqdm
import csv
import urllib

#download data from alaska website
file = urllib.URLopener()
testfile.retrieve("http://www.elections.alaska.gov/results/16GENR/data/resultsbyprct.txt", "resultsbyprct.txt")


#read in data and save lines for presidential and district races

pres_lines = []
dist_lines = []

with open("resultsbyprct.txt") as f:
    for line in f:
        line = line.split(",")
        line = line[:-1]
        line = [l[1:-2] for l in line[:-1]] + [line[-1]]

        if line[0][:4] == "Dist" or line[0][:4] == "HD99" :
            pass
        elif line[1] == 'US PRESIDENT':
            pres_lines.append(line)

        elif line[1][:5] == 'HOUSE':
            dist_lines.append(line)
        else:
            pass


#loop over precincts and gather data for each precinct

precincts = list(set([l[0] for l in pres_lines]))

dem_pres_vote = []
rep_pres_vote = []
o_pres_vote = []

dem_dist_vote = []
rep_dist_vote = []
o_dist_vote = []

dists = []

contested = []


for precinct in precincts:
    pres_results = filter(lambda x : x[0] == precinct, pres_lines)

    dem = filter(lambda x : x[4] == 'DEM', pres_results)[0][-1]
    rep = filter(lambda x : x[4] == 'REP', pres_results)[0][-1]
    dem_pres_vote.append(dem)
    rep_pres_vote.append(rep)


    other = filter(lambda x : x[4] in ["CON", "NA", "GRE", "LIB"], pres_results)
    other = sum([int(o[-1]) for o in other])
    o_pres_vote.append(other)

    dist_results = filter(lambda x : x[0] == precinct, dist_lines)

    dist = dist_results[0][1].split(" ")
    if dist[-1] != "":
        dists.append(dist[-1])
    else:
        dists.append(dist[-2])

    dem = filter(lambda x : x[4] == 'DEM', dist_results)
    rep = filter(lambda x : x[4] == 'REP', dist_results)

    if len(dem)!=0 and len(rep)!= 0:
        contested.append("B")
        dem_dist_vote.append(dem[0][-1])
        rep_dist_vote.append(rep[0][-1])

    elif len(dem)!=0 and len(rep)==0:
        contested.append("D")
        dem_dist_vote.append(dem[0][-1])
        rep_dist_vote.append("NA")

    elif len(dem)==0 and len(rep)!=0:
        contested.append("R")
        dem_dist_vote.append("NA")
        rep_dist_vote.append(rep[0][-1])
    else:
        contested.append("O")
        dem_dist_vote.append("NA")
        rep_dist_vote.append("NA")


#organize data and write to csv
codes = map(lambda x : x[:6], precincts)
names = map(lambda x : x[6:], precincts)

data = zip(codes, names, dists, dem_pres_vote, rep_pres_vote,
           o_pres_vote, dem_dist_vote, rep_dist_vote, contested)
data = sorted(data, key = lambda x : float(x[2]))


with open("data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Code", "Name", "District", "D-Pres Vote", "R-Pres Vote",
                     "TP-Pres Vote", "D-Dist Vote", "R-Dist Vote", "Contested"])
    for j in range(len(data)):
        writer.writerow(data[j])

with open("contested_data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Code", "Name", "District", "D-Pres Vote", "R-Pres Vote",
                     "TP-Pres Vote", "D-Dist Vote", "R-Dist Vote", "Contested"])

    contested_data = filter(lambda x : x[-1] == "B", data)
    for j in range(len(contested_data)):
        writer.writerow(contested_data[j])
