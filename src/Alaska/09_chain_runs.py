#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 10:42:44 2018

@author: samirkhan
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from copy import copy
import csv
from tqdm import tqdm
from sklearn.model_selection import cross_val_score
import pickle

#load in the model and the data
with open("2014data.pkl", "rb") as f:
    df = pickle.load(f)

with open("logistic_model.pkl", "rb") as f:
    model = pickle.load(f)

#a function that pre-computes probabilities for all the pairings in a list of matchings given a list of the matchings,
#a model, and data for districts. These should be in the form of a list of lists of tuples, an sklearn object, and a pandas df respectively.
def log_matchings(matchings, model, district_data):
    log = {}

    for match in matchings:
        if match in log.keys():
            pass

        else:
            d1 = district_data[district_data["New District"] == int(match[0])]
            d2 = district_data[district_data["New District"] == int(match[1])]
            d = np.array(d1) + np.array(d1)
            d = pd.DataFrame(d[:,1:])
            d.columns = ["Dem. Sen.", "Rep. Sen.", "sumTOTALPOP",
                         "sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"]


            d2 = copy(d)

            #Adjusting demographic columns to be percentages
            for col in ["sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"]:
                d2[col] = d[col]/d["sumTOTALPOP"]



            #Adjusting vote columns to be percentages

            d2["Dem. Sen."] = d["Dem. Sen."]/(d["Dem. Sen."]+d["Rep. Sen."])
            d2["Rep. Sen."] = d["Rep. Sen."]/(d["Dem. Sen."]+d["Rep. Sen."])

            X = d2[["Dem. Sen.", "Rep. Sen.", "sumWHITE", "sumBLACK",
                    "sumNATIVE", "sumASIAN"]].as_matrix()

            prob = model.predict_proba(X)[0][1]

            log[match] = prob
    return log


#This function loops over all matchings of a districting and returns the expected seats for each.
#A districting is a dictionary from GEOIDs to district number, and matchings is a list of list of tuples. 
def expected_seats(districting, matchings):
    #Add new districts as a column
    df2 = copy(df)
    df2["New District"] = df2["Code"].map(districting)

    #Save data aggregated by district
    rows = []
    for j in range(1,41):
        vals = list(df[df["New District"] == j][["Dem. Sen.", "Rep. Sen.", "sumTOTALPOP",
                                 "sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"]].sum(axis=0))
        rows.append([j]+vals)
    df_dist = pd.DataFrame(rows, columns = ["Dem. Sen.", "Rep. Sen.", "sumTOTALPOP",
                                 "sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"])

    #Make log of matchings
    L = log_matchings(matchings, model, df_dist)


    all_seats = []
    for matching in matchings:
        seats = 0
        for match in matching:
            outcome = L[match]
            seats += outcome
        all_seats.append(seats)

    return all_seats
