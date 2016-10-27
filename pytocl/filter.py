import numpy as np

#K = 1
#T = 0.5

def pt1up(K,T,x):
    return K*(1-np.exp(-x/T))

def pt1down(K,T,x):
    return 1-(K*(1-np.exp(-x/T)))
