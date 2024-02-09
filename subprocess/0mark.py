import numpy as np
import pandas as pd
import polars as pl
import plotly.express as px

amplitude = 1000
Fs = 360
sample = 1500
step = 360/sample
x = np.arange(0,360,step)
yR = amplitude * (np.sin(2*np.pi*x/Fs))
yS = amplitude * (np.sin((2*np.pi*x/Fs)+180))
yT = amplitude * (np.sin((2*np.pi*x/Fs)-180))
y = np.concatenate((yR,yS,yT))
x = np.concatenate((x,x,x))

kind = []
for element in x:
    kind.append("sine")

df0 = pl.DataFrame({'x':x,'y':y,'kind':kind})

df = pl.read_csv('file2.csv')
yArr = df['y'].to_numpy()
maxValueIndex = yArr.argmax(axis = 0)
print(maxValueIndex)
print(yArr)

half = int(len(df)/2)
quarter = int(len(df)/4)
thirdqua = int(len(df)*3/4)

if maxValueIndex  <= quarter:
    quadrant11 = yArr[(maxValueIndex + thirdqua):]
    quadrant12 = yArr[:maxValueIndex]
    quadrant1 = np.concatenate((quadrant11, quadrant12))
    quadrant2 = yArr[maxValueIndex:(maxValueIndex + quarter)]
    quadrant3 = yArr[(maxValueIndex + quarter):(maxValueIndex + half)]
    quadrant4 = yArr[(maxValueIndex + half):(maxValueIndex + thirdqua)]
elif maxValueIndex <= half:
    quadrant1 = yArr[(maxValueIndex - quarter):maxValueIndex]
    quadrant2 = yArr[maxValueIndex:(maxValueIndex + quarter)]
    quadrant3 = yArr[(maxValueIndex + quarter):(maxValueIndex + half)]
    quadrant41 = yArr[(maxValueIndex + half):]
    quadrant42 = yArr[:(maxValueIndex - quarter)]
    quadrant4 = np.concatenate((quadrant41,quadrant42))
elif maxValueIndex <= thirdqua:
    quadrant1 = yArr[(maxValueIndex - quarter):maxValueIndex]
    quadrant2 = yArr[maxValueIndex:(maxValueIndex + quarter)]
    quadrant31 = yArr[(maxValueIndex + quarter):]
    quadrant32 = yArr[:(maxValueIndex - half)]
    quadrant3 = np.concatenate((quadrant31,quadrant32))
    quadrant4 = yArr[(maxValueIndex - half):(maxValueIndex - quarter)]
else:
    quadrant1 = yArr[(maxValueIndex - quarter):maxValueIndex]
    quadrant21 = yArr[maxValueIndex:]
    quadrant22 = yArr[:(maxValueIndex - thirdqua)]
    quadrant2 = np.concatenate((quadrant21,quadrant22))
    quadrant3 = yArr[(maxValueIndex - thirdqua):(maxValueIndex - half)]
    quadrant4 = yArr[(maxValueIndex - half):(maxValueIndex - quarter)]

yArrR = np.concatenate((quadrant1,quadrant2,quadrant3,quadrant4))
pertama = yArrR[:(int(len(yArrR)*1/3))]
kedua = yArrR[int(len(yArrR)*1/3):int(len(yArrR)*2/3)]
ketiga = yArrR[int(len(yArrR)*2/3):]
yArrS = np.concatenate((kedua,ketiga,pertama))
yArrT = np.concatenate((ketiga,pertama,kedua))

xArr = np.arange(0,360,360/len(yArrR))

kind = []
for element in xArr:
    kind.append('sens')

# numpy
xsens = np.reshape(xArr, (-1,1))
ysens = np.reshape(yArrR, (-1,1))
ksens = np.reshape(kind, (-1,1))
sens = np.concatenate((xsens, ysens, ksens), axis=1, dtype=object)
fsens = sens[ ((sens[:,1] > 300) | (sens[:,1] < -300)) & (sens[:,2] == 'sens') ]
sine = df0.get_column(['x','y','kind']).to_numpy()

combine = np.concatenate((sine,fsens))

fig = px.scatter(x = combine[:,0], 
                 y = combine[:,1],
                 color = combine[:,2])
# fig.show()


# polar
"""
df1 = pl.DataFrame({'x':xArr,'y':yArrR,'kind':kind})
df1 = df1.filter(((pl.col("y") > 450) & pl.col("kind").is_in(["sens"])) |
                 ((pl.col("y") < -450) & pl.col("kind").is_in(["sens"])) |
                 (pl.col("kind").is_in(["sine"]))
)

dfn = df0.vstack(df1)
print(len(dfn))

fig = px.scatter(x = dfn.select('x').to_series(), 
                 y = dfn.select('y').to_series(),
                 color = dfn.select('kind').to_series())
fig.show()
"""
