import numpy as np
import pandas as pd
import plotly.express as px
import time

amplitude = 1000
Fs = 360
sample = 1500
step = 360/sample
x = np.arange(0,360,step)
y = amplitude * (np.sin(2*np.pi*x/Fs))
kind = []
for element in x:
    kind.append("sine")
df0 = pd.DataFrame({'x':x,'y':y,'kind':kind})

df = pd.read_csv('file2.csv')
# print(df)
# maxvalue = df['y'].max()
maxValueIndex = df['y'].idxmax()
yArr = df['y'].to_numpy()

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
channel2 = np.concatenate((quadrant1,quadrant2,quadrant3,quadrant4))
xArr = np.arange(0,360,360/len(channel2))
kind = []
for element in xArr:
    kind.append("sens")
df1 = pd.DataFrame({'x':xArr,'y':channel2,'kind':kind})

df1 = df1[
    ((df1['y'] > 300) & df1['kind'].isin(['sens'])) |
    ((df1['y'] <-300) & df1['kind'].isin(['sens'])) |
    df1['kind'].isin(['sine'])
]

dfn = pd.concat([df0, df1], axis=0)

# fig = px.scatter(x=xArr, y=channel2)
fig = px.scatter(dfn, x='x', y='y')
fig.show()
# fig = px.scatter(x=x, y=y)
# fig.show()