import numpy as np
import random

data = np.load('AllSamples.npy')

def initial_point_idx2(id,k, N):
    random.seed((id+k))     
    return random.randint(0,N-1)    

def initial_S2(idx,k):
    # print("Strategy 2: k and initial points")
    i = int(idx)%150 
    random.seed(i+800)
    init_idx2 = initial_point_idx2(i, k,data.shape[0])
    init_s2 = data[init_idx2,:]
    return init_s2

def init_point(data, idx):
    return data[idx,:]
