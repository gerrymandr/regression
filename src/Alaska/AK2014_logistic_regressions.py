#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 10:00:49 2018

@author: samirkhan
"""

import pandas as pd 
from sklearn.linear_model import LogisticRegression
import numpy as np
from copy import copy
import csv 
from tqdm import tqdm
from sklearn.model_selection import cross_val_score

#Loading in data
df = pd.read_csv("2014AKDataByPrecinct.csv")

#Helper function to convert vote counts to race outcome
def compare_results(row):
    if np.isnan(row["Dem. Dist."]):
        return False
    elif np.isnan(row["Rep. Dist."]):
        return True 
    else:
        return row["Dem. Dist."]>row["Rep. Dist."]

#Marking down results by precinct
df["Prec. Res."] = df.apply(lambda row: compare_results(row), axis = 1)


#Making a copy we can change things in
df2 = copy(df)

#Adjusting demographic columns to be percentages
for col in df.columns[14:25]:
    df2[col] = df[col]/df["sumTOTALPOP"]


    
#Adjusting vote columns to be percentages    
df2["Dem. Dist."] = df["Dem. Dist."]/(df["Dem. Dist."]+df["Rep. Dist."])    
df2["Rep. Dist."] = df["Rep. Dist."]/(df["Dem. Dist."]+df["Rep. Dist."])    

df2["Dem. Sen."] = df["Dem. Sen."]/(df["Dem. Sen."]+df["Rep. Sen."])    
df2["Rep. Sen."] = df["Rep. Sen."]/(df["Dem. Sen."]+df["Rep. Sen."])    




#Picking out some features and the response 
X = df2[df2["Contested"] == "B"][["Dem. Sen.", "Rep. Sen.", "sumWHITE", "sumBLACK", 
                                  "sumNATIVE", "sumASIAN"]].as_matrix()
y = df2[df2["Contested"] == "B"]["Prec. Res."]
y = np.array(map(lambda x : 1 if x else 0, y))


#Fit and evaluate logistic regression
model = LogisticRegression(penalty = "l1", C=50)
model.fit(X, y)
y_hat = model.predict(X)
print "%.0f out of %.0f right in training" % (sum(y==y_hat), len(y))
print np.mean(cross_val_score(model, X, y))


#Try all the elections, not just contested ones
X_all = df2[["Dem. Sen.", "Rep. Sen.", "sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"]].as_matrix()
y_all = df2["Prec. Res."]
y_all = np.array(map(lambda x : 1 if x else 0, y_all))
y_all_hat = model.predict(X_all)
print "%.0f out of %.0f right in testing" % (sum(y_all==y_all_hat), len(y_all))


#Save data aggregated by district
#with open("district_data.csv", "w") as f:
#    writer = csv.writer(f)
#    writer.writerow(["District", "Dem. Sen.", "Rep. Sen.", "sumTOTALPOP",
#                     "sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"])
#    for j in range(1,41):
#        vals = list(df[df["District"] == j][["Dem. Sen.", "Rep. Sen.", "sumTOTALPOP",
#                                 "sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"]].sum(axis=0))
#        writer.writerow([j]+vals)

 
#Load in data aggregated by district
district_data = pd.read_csv("district_data.csv")
    
#Helper function that turns list of counties into list of match pairs
def make_matching(l):
    return [l[i:i+2] for i in range(0, len(l)-1, 2)]

#For a single matching, loop over pairs and predict winner for each senate district
def evaluate_matching(matching, model):
    seats = 0
    for match in matching:
        d1 = district_data[district_data["District"] == int(match[0])]
        d2 = district_data[district_data["District"] == int(match[1])]
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
        outcome = model.predict(X)
        seats += outcome
    
    return seats[0]        

#Loop over all matchings, and keep track of number of seats won     
def check_all_matchings(model):    
    seats = []
    with open("AKallpairings.csv") as f:
        reader = csv.reader(f)
        for row in tqdm(reader):
            #for each matching, compute and save statistics 
            matching = make_matching(row)
            match_seats = evaluate_matching(matching, model)    
            seats.append(match_seats)
    
    return seats
 
#alignments = {}    
#for j in range(1,41):
#    d = district_data[district_data["District"] == j]
#    
#    d2 = copy(d)
#    
#    #Adjusting demographic columns to be percentages
#    for col in ["sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"]:
#        d2[col] = d[col]/d["sumTOTALPOP"]
#    
#    
#        
#    #Adjusting vote columns to be percentages    
#    
#    d2["Dem. Sen."] = d["Dem. Sen."]/(d["Dem. Sen."]+d["Rep. Sen."])    
#    d2["Rep. Sen."] = d["Rep. Sen."]/(d["Dem. Sen."]+d["Rep. Sen."])
#    
#    X = d2[["Dem. Sen.", "Rep. Sen.", "sumWHITE", "sumBLACK", 
#            "sumNATIVE", "sumASIAN"]].as_matrix()
#    outcome = model.predict_log_proba(X)[0]
#    alignments[j] = np.exp(outcome[1])
#    
#with open("district_alignments.csv", "w") as f:
#    writer = csv.writer(f)
#    writer.writerow(["District", "Prob. Dem."])
#    for j in range(1,41):
#        writer.writerow([j, alignments[j]])
    
    
        
    
