### DO NOT CHANGE ANYTHING IN THIS FILE. TREAT IT AS A READ-ONLY FILE.

import numpy as np
import random

data = np.load('AllSamples.npy')

def initial_point_idx(id, k,N):
	return np.random.RandomState(seed=(id+k)).permutation(N)[:k]

def init_point(data, idx):
    return data[idx,:]

def initial_S1(id, k):
    # print("Strategy 1: k and initial points")
    i = int(id)%150 
    random.seed(i+500)
    init_idx = initial_point_idx(i,k,data.shape[0])
    init_s1 = init_point(data, init_idx)
    return init_s1
