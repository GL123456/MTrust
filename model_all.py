#! /usr/bin/env python


import sys
import copy
import os
import numpy as np
from data_handler import data_handler
import tables as tb
import math
import pdb


CURRENT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./")

class mTrust():

    def __init__(self):
        # Loading matrices from given data
        data = data_handler(CURRENT_DIR + "data/rating_with_timestamp.mat", CURRENT_DIR + "data/trust.mat")
        #data = data_handler("data/ciao/rating_with_timestamp.mat", "data/ciao/trust.mat")
        self.R_train, self.R_test, self.W, self.PF, self.mu = data.load_matrices()
        # Getting unique users and products used in Training data
        self.prod = np.unique(self.R_train[:, 1])
        self.users = np.unique(self.R_train[:, 0])
        #print self.prod
        self.n_users, self.n_prod, self.n_cat = data.get_stats()
        common_users = np.intersect1d(self.R_test[:, 0], self.users)
        common_prod = np.intersect1d(self.R_test[:, 1], self.prod)
        self.R_test = self.R_test[np.in1d(self.R_test[:, 0], common_users)]
        self.R_test = self.R_test[np.in1d(self.R_test[:, 1], common_prod)]
        # Creating R_train and R_test dictionaries
        self.R_train_ui = dict(zip(zip(self.R_train[:, 0], self.R_train[:, 1]), self.R_train[:, 3])) 



        x_R_train_ui={}
        for i in range(1000):
            for j in range(1000):
                x_R_train_ui[i,j]=0
        for i in range(100):
            for j in range(100):
                pass
                #print i,j
                #x_R_train_ui[(R_train[:,0][i],x_R_train[:,1][j])]=x_R_train[:,3][i]





        self.R_test_ui = dict(zip(zip(self.R_test[:, 0], self.R_test[:, 1]), self.R_test[:, 3]))
        


        x_R_test_ui={}
        for i in range(1000):
            for j in range(1000):
                x_R_test_ui[(i,j)]=0
        for i in range(100):
            pass
                #print i,j
                #self.R_test_ui[(self.R_test[:,0][i],self.R_test[:,1][j])]=self.R_test[:,3][i]
        








        #print self.R_train_ui
        self.A = np.zeros((self.n_users + 1, self.n_users + 1, self.n_cat))
        for u, v in self.W:
            #print str(u) + " " + str(v)
            self.A[v, u, :] = 1
        print self.n_users
        
        
        self.C = np.random.rand(1001)
        self.E = copy.deepcopy(self.R_train_ui)
        self.B = np.random.rand(1001, self.n_cat)


        self.V = {}
        #self.getNui()
        self.Nui()
        self.alpha = float(sys.argv[1])
        self.l = float(sys.argv[2])

    def Nui(self):
        with open('./data/nui') as f:
        #with open('../data/ciao/ciaonui') as f:
            content = f.readlines()
            for line in content:
                line = line.split('\n')[0]
                value = map(int, line.split('[')[1].split(']')[0].split())
                #print value
                key = (int(line.split(' ')[0]), int(line.split(' ')[1]))
                value_x = [r for r in value if r < 1000]
                #print key[0],key[1]
                #print key
                #print value
                #print "\n"
                self.V[key] = value
        
    
    def calc_cost(self):
        cost = sum(self.E[key] * self.E[key] for key in self.E)
        cost += self.l*(np.vdot(self.B, self.B) + np.vdot(self.C, self.C))
        return cost


    def model(self, lr_a = 0.1, lr_b = 0.1, lr_c = 0.1, n_it = 100):
        self.Rcap = np.zeros_like(self.R_train_ui)
        cat_map = {0:7, 1:8, 2:9, 3:10, 4:11, 5:19}
        #cat_map = {0:8, 1:14, 2:17, 3:19, 4:23, 5:24}
        for it in xrange(n_it):
            cost = self.calc_cost()
            for u, i in self.R_train_ui:
                Rcap = self.calculateRcap(u, i)
                # Defining E
                self.E[u, i] = self.R_train_ui[(u, i)] - Rcap
                # Updating C
                grad_c = (-self.alpha * self.E[u, i]) + (self.l * self.C[i])
                self.C[i] -= (lr_c * grad_c)
                # Updating B
                d = 0
                for k in xrange(self.n_cat):
                    if (i,cat_map[k]) in self.PF:
                        d += 1
                #print self.B[u,:]
                grad_b = (-self.alpha * self.E[u, i]) + (self.l * (self.B[u, :]/d))
                #grad_b = -self.alpha * (self.E[u, i]/d) + self.l * self.B[u, :]
                self.B[u, :] -= (lr_b * grad_b)
                # Updating A
                for k in xrange(self.n_cat):
                    if (i,cat_map[k]) in self.PF:
                        for v in self.V[u, i]:
                            if self.p != 0:
                                grad_a = ((self.alpha - 1) * self.E[u,i] ) * (((self.p * self.R_train_ui[v, i]) - self.q)/(self.p * self.p))
                                self.A[v, u, k] -= (lr_a * grad_a)
                                if self.A[v, u, k] < 0:
                                    self.A[v, u, k] = 0
                                elif self.A[v, u, k] > 1:
                                    self.A[v, u, k] = 1
            print "Iteration: ", it+1, " Training Cost: ", cost, "RMSE (test): ", self.test() 

    def calculateRcap(self, u, i):
        cat_map = {0:7, 1:8, 2:9, 3:10, 4:11, 5:19}
        #cat_map = {0:8, 1:14, 2:17, 3:19, 4:23, 5:24}
        # First part of Rcap
        n1 = 0
        d1 = 0
        Rcap=0
        n2 = 0
        d2 = 0
        alp=(1-self.alpha)
        for k in xrange(self.n_cat):
            if (i,cat_map[k]) in self.PF:
                n1 += (self.mu[k] + self.B[u, k])
                d1 += 1
        if d1 !=0:
            Rcap = self.alpha * ((n1/d1) + self.C[i])
        # Second part of Rcap
        for k in xrange(self.n_cat):
            if((i,cat_map[k]) in self.PF):
                for v in self.V[u, i]:
                    #print self.A[v,u,k]
                    n2 += (self.R_train_ui[v, i] * self.A[v, u, k])
                    d2 += self.A[v, u, k]
        if d2 != 0:
            Rcap += (alp * (n2/d2))
        # Defining p and q
        self.p = d2
        self.q = n2
        return Rcap

    
    
    def test(self):
        error = 0
        U = 0
        for key in self.R_test_ui:
            U += 1
            u, i = key
            error += math.pow(self.R_test_ui[u, i] - self.calculateRcap(u, i),2)
            #error += (R_Rcap * R_Rcap)
        return math.sqrt(error/U)
    
def main():
    model = mTrust()
    model.model()

if __name__ == "__main__":
    main()
