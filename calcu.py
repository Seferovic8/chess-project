import numpy as np
def calculate_padding(K,S,W=8):
    return ((W-1)*S-W+K)/2
def calculate_output(K,S,P,W=8):
    return (W-K+2*P)/S + 1
W=7
K=2
S=1
padding = calculate_padding(K=K,S=S,W=W)
padding=0
output=calculate_output(K=K,S=S,P=padding,W=W)
print(f"Padding: {padding}, Output:{output}")