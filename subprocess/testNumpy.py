import numpy as np
import plotly.express as px

amplitude = 1000
Fs = 360
sample = 1500
step = 360/sample
x = np.arange(0,360,step)
yR = amplitude * (np.sin(2*np.pi*x/Fs))
yS = amplitude * (np.sin((2*np.pi*x/Fs)+180))
yT = amplitude * (np.sin((2*np.pi*x/Fs)-180))
x = np.concatenate((x,x,x))
y = np.concatenate((yR,yS,yT))
sineSign = np.concatenate((np.repeat(1,len(yR)), np.repeat(2,len(yS)), np.repeat(3,len(yT))), axis=0)

sineSet = np.concatenate((x.reshape(len(x),1), y.reshape(len(y),1), sineSign.reshape(len(sineSign),1)), axis=1)
print(len(sineSet))

arr = np.loadtxt("file3.csv",
                 delimiter=",",
                 dtype=float)
# slicing
arr1 = arr[1:]

# indexing
idx = arr1[0,1]

# create one
ones = np.ones(len(arr1),dtype=int).reshape(len(arr1),1)
buah = np.append(arr1,ones,axis=1) 
# print(np.repeat(2,len(arr1)))

# print(arr1)
# print(len(arr1))
# print(arr1.shape)

# print(ones)
# print(len(ones))
# print(ones.shape)

# print(buah)
# print(len(buah[:,0]))
# print(len(buah[:,1]))

# fig = px.scatter(x=buah[:,0], y=buah[:,1])
# fig.show()

mask = (buah[:,1] > 0)
# print(buah[mask])