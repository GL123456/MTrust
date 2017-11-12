#!/bin/python

import sys
import os
import subprocess

# This script should be run from the folder ./epinions/epinions/epinions/

user_list = []   # list of all the users
reviews = {}     # key : userID ,val : list of lists, each list contain values (producttext, categorytext, productrating, reviewrating)
trusts = {}   # key : userID ,val : list of all other users
trustedby = {}   # key : userID ,val : list of other users

# Extract all the userID present in data

user_list = subprocess.check_output("ls userpages/", shell = True)
user_list = user_list.split("\n");
for i,user in enumerate(user_list):
    user_list[i] = user[:-5]
user_list.remove('')
print "List of Users extracted"

# For extracting reviews of all the users to reviews dictionary
for user in user_list:
    path = "./reviews/" + user
    lst = []
    temp_review_data = open(path, "r+").readlines()
    for line in temp_review_data:
        line = line.split("\t")
        producttext = line[3]
        categorytext = line[5]
        productrating = line[7]
        reviewrating = line[8]
        temp_list = []
        temp_list.append(producttext)
        temp_list.append(categorytext)
        temp_list.append(productrating)  # It can be 'na' also
        temp_list.append(reviewrating)
        lst.append(temp_list)
    reviews[user] = lst

print "All the reviews extracted"

#For extracting followers and following
for user in user_list:
    path = "./wot/" + user
    temp_trusts = []
    temp_trustedby = []
    path_trusts = path + "-trusts"
    path_trustedby = path + "-trustedby"
    data_trusts = open(path_trusts, "r+").readlines()
    data_trustedby = open(path_trustedby, "r+").readlines()
    for temp in data_trusts:
        temp = temp.split("\t")[0]
        temp_trusts.append(temp)
    for temp in data_trustedby:
        temp = temp.split("\t")[0]
        temp_trustedby.append(temp)
    trusts[user] = temp_trusts
    trustedby[user] = temp_trustedby

print "All the trusts and trustedby values extracted"


