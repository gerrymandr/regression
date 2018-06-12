#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 21:46:50 2018

@author: samirkhan
"""

import csv
import urllib
#this script merges voting data scraped from 01a_scraper.py with demographic data (obtained by GIS)

file = urllib.URLopener()
file.retrieve("https://www.dropbox.com/home/Gerrycamp%20Regressions%20Project/Alaska%20Project?preview=AKDemDataByPrecinct.csv", "AKDemDataByPrecinct.csv")


#read in and store both files
dem_data = []
vote_data = []

with open("AKDemDataByPrecinct.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        dem_data.append(row)

with open("AKVoteDataByPrecinct.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        vote_data.append(row)

dem_labels = dem_data.pop(0)
vote_labels = vote_data.pop(0)

#write the results back out in one csv
with open("AKADataByPrecinct.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(vote_labels+dem_labels[:2]+dem_labels[6:])
    for j in range(len(vote_data)):
        row = vote_data[j]
        match_row = filter(lambda x : x[2] == row[0], dem_data)[0]
        writer.writerow(row+match_row[:2]+match_row[6:])
