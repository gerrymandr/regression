#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 10:00:49 2018

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

labels = {0:"12", 1:"29", 2:"17", 3:"38", 4:"5", 5:"8", 6:"23", 7:"31", 8:"33", 9:"04", 10:"39",
          11:"10", 12:"09", 13:"24", 14:"32", 15:"03", 16:"16", 17:"21", 18:"37", 19:"40", 20:"35",
          21:"06", 22:"07", 23:"34", 24:"14", 25:"27", 26:"20", 27:"26", 28:"19", 29:"36", 30:"25",
          31:"28", 32:"01", 33:"02", 34:"11", 35:"18", 36:"15", 37:"30", 38:"13", 39:"22"}                

#Loading in data
df = pd.read_csv("2014AKDataByPrecinct.csv")
with open("alaska_matchings.pkl") as f:
    ak_matchings = pickle.load(f)
    
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
#model = KNeighborsClassifier(n_neighbors=3)
#model = SVC(C=50)
model = LogisticRegression(penalty = "l1", C=2)
model.fit(X, y)
y_hat = model.predict(X)
print "Training Accuracy: %.0f out of %.0f" % (sum(y==y_hat), len(y))


#Try all the elections, not just contested ones
X_all = df2[["Dem. Sen.", "Rep. Sen.", "sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"]].as_matrix()

y_all = df2["Prec. Res."]
y_all = np.array(map(lambda x : 1 if x else 0, y_all))
y_all_hat = model.predict(X_all)
print "Testing Accuracy: %.0f out of %.0f" % (sum(y_all==y_all_hat), len(y_all))

print "Cross-Validation Score: %.3f" % np.mean(cross_val_score(model, X, y, cv=5))


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
    
df_dist = copy(district_data)

#Adjusting demographic columns to be percentages
for col in ["sumWHITE", "sumBLACK", "sumNATIVE", "sumASIAN"]:
    df_dist[col] = district_data[col]/district_data["sumTOTALPOP"]


    
#Adjusting vote columns to be percentages    

df_dist["Dem. Sen."] = district_data["Dem. Sen."]/(district_data["Dem. Sen."]+district_data["Rep. Sen."])    
df_dist["Rep. Sen."] = district_data["Rep. Sen."]/(district_data["Dem. Sen."]+district_data["Rep. Sen."])

#Helper function that turns list of counties into list of match pairs
#def make_matching(l):
#    return [l[i:i+2] for i in range(0, len(l)-1, 2)]

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
        
        prob = model.predict_proba(X)[0][1]
        
        seats += prob
    
    return seats         


def match_to_string(match):
    return "%s %s" % tuple(match)

def log_matchings():
    log = {}     
    for matching in ak_matchings:            
        for match in matching:   
            m = (int(labels[match[0]-1]), int(labels[match[1]-1]))
            
            if m in log.keys():
                pass            
            else:
                d1 = district_data[district_data["District"] == m[0]]
                d2 = district_data[district_data["District"] == m[1]]
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
                
                log[m] = prob
    return log 
            

    

#Loop over all matchings, and keep track of number of seats won     
def check_all_matchings(model, log):  
    all_seats = []    
    for matching in tqdm(ak_matchings):
        seats = 0
        for match in matching:
            m = (int(labels[match[0]-1]), int(labels[match[1]-1]))
            if m in log.keys():
                outcome = log[m]
            else:
                outcome = log[(m[1], m[0])]
            seats += outcome 
        all_seats.append(seats)
                
            
#            for j in range(100):
#                match_seats = 0
#                for match in matching:
#                    p = log[match_to_string(match)]
#                    match_seats += np.random.binomial(1, p)
#                seats.append(match_seats)
                    
    return all_seats
 
import matplotlib.pyplot as plt 
L = log_matchings()
true_matching = [(j, j+1) for j in range(1, 41, 2)]
t = evaluate_matching(true_matching, model)
s = check_all_matchings(model, L)
plt.hist(s, bins=100)
plt.axvline(t, c="r")    


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
    
    
        
