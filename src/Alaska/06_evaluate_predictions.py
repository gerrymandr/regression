#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 13:31:26 2018

@author: samirkhan
"""

import csv

#dictionaries to keep track of things
results = {}
incumbencies = {}
contested = {}

#populating dictionaries with data from the big csv
with open("AKDataByPrecinct.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if row[3] in results.keys():
            pass
        else:
            results[row[3]] = row[-6]

            if row[-7] == "1":
                incumbencies[row[3]] = "R"
            elif row[-8] == "1":
                incumbencies[row[3]] = "D"
            else:
                incumbencies[row[3]] = "N"

            contested[row[3]] = row[9]




def evaluate_prediction(filename):
    pred_results = {}

    #reading in file with vote counts and getting predicted results
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if float(row[1]) > float(row[2]):
                pred_results[row[0]] = "D"
            else:
                pred_results[row[0]] = "R"

    #writing true result, preicted result, and other values to a csv
    with open("evaluation.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["District", "True Winner", "Pred. Winner", "Correct?", "Contested", "Incumbent"])
        for j in range(1,41):
            js = str(j)
            writer.writerow([js, results[js], pred_results[js], int(results[js]==pred_results[js]),
                             int(contested[js]=="B"), int(incumbencies[js] != "N")])
