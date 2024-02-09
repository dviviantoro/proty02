import time
import json
import redis
import streamlit as st
import plotly.express as px
import datetime
import numpy as np

json_path = 'subprocess/data.json'
r = redis.Redis(host='localhost', port=6379, db=0)

st.set_page_config(page_title="Databases", page_icon="🐌", layout="wide")
st.markdown("# Databases")

def load_json(object1, object2):
    arr = []
    with open(json_path, 'r') as openfile:
        json_object = json.load(openfile)
    for project in json_object[object1]:
        options = project[object2]
        arr.append(options)
    return arr

def form_bgn(object):
    global project_bgn, chartR_bgn, chartS_bgn, chartT_bgn, summR_bgn, summS_bgn, summT_bgn, data_json_bgn

    placeholder = st.empty()
    with placeholder.container():
        col1, col2 = st.columns([1,3])
        project_bgn = col1.selectbox('Project background', load_json(object, "project"))
        data_json_bgn = col1.empty()

        tab1, tab2, tab3 = col2.tabs(["Phase R", "Phase S", "Phase T"])
        with tab1:
            chartR_bgn = st.empty()
            summR_bgn = st.empty()
        with tab2:
            chartS_bgn = st.empty()
            summS_bgn = st.empty()
        with tab3:
            chartT_bgn = st.empty()
            summT_bgn = st.empty()
        show_bgn("background")

def show_bgn(obj):
    idx_project = load_json(obj, "project").index(project_bgn)
    a_file = open(json_path, "r")
    json_object = json.load(a_file)

    xaxis_title = "count"
    data_json_bgn.json({
        'project': project_bgn,
        'operator': json_object[obj][idx_project]["operator"],
        'hfct_model': json_object[obj][idx_project]["sensor"],
        'count': len(json_object[obj][idx_project]["xaxis"])
    })
    try:
        xaxis = json_object[obj][idx_project]["xaxis"]

        volR_pos = np.array([x for x in json_object[obj][idx_project]["volR"] if x>0])
        kind = []
        for element in volR_pos: kind.append('bgnR_pos')
        arrVolR_pos = np.concatenate((np.reshape(xaxis,(-1,1)),np.reshape(volR_pos,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

        volR_neg = np.array([x for x in json_object[obj][idx_project]["volR"] if x<0])
        kind = []
        for element in volR_neg: kind.append('bgnR_neg')
        arrVolR_neg = np.concatenate((np.reshape(xaxis,(-1,1)),np.reshape(volR_neg,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

        arrVolR = np.vstack((arrVolR_pos,arrVolR_neg))

        figR = px.line(x=arrVolR[:,0], y=arrVolR[:,1], color=arrVolR[:,2], markers=True)
        figR.update_layout(xaxis_title=xaxis_title,yaxis_title="voltage (mV)")
        figR.update_xaxes(showgrid=False)
        figR.update_yaxes(showgrid=False)

        chartR_bgn.plotly_chart(figR, use_container_width=True)
        summR_bgn.json({'max_bgn':round(np.max(volR_pos),3),'min_bgn':round(np.min(volR_neg),3)})

        # volS_pos = np.array([x for x in json_object[obj][idx_project]["volS"] if x>0])
        # kind = []
        # for element in volS_pos: kind.append('bgnS_pos')
        # arrVolS_pos = np.concatenate((np.reshape(xaxis,(-1,1)),np.reshape(volS_pos,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)
        
        # volS_neg = np.array([x for x in json_object[obj][idx_project]["volS"] if x<0])
        # kind = []
        # for element in volS_neg: kind.append('bgnS_neg')
        # arrVolS_neg = np.concatenate((np.reshape(xaxis,(-1,1)),np.reshape(volS_neg,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)
            
        # arrVolS = np.vstack((arrVolS_pos,arrVolS_neg))

        # volT_pos = np.array([x for x in json_object[obj][idx_project]["volT"] if x>0])
        # kind = []
        # for element in volT_pos: kind.append('bgnT_pos')
        # arrVolT_pos = np.concatenate((np.reshape(xaxis,(-1,1)),np.reshape(volT_pos,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)
        
        # volT_neg = np.array([x for x in json_object[obj][idx_project]["volT"] if x<0])
        # kind = []
        # for element in volT_neg: kind.append('bgnT_neg')
        # arrVolT_neg = np.concatenate((np.reshape(xaxis,(-1,1)),np.reshape(volT_neg,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

        # arrVolT = np.vstack((arrVolT_pos,arrVolT_neg))

        # figS = px.line(x=arrVolS[:,0], y=arrVolS[:,1], color=arrVolS[:,2], markers=True)
        # figS.update_layout(xaxis_title=xaxis_title,yaxis_title="voltage (mV)")
        # figS.update_xaxes(showgrid=False)
        # figS.update_yaxes(showgrid=False)
        
        # figT = px.line(x=arrVolT[:,0], y=arrVolT[:,1], color=arrVolT[:,2], markers=True)
        # figT.update_layout(xaxis_title=xaxis_title,yaxis_title="voltage (mV)")
        # figT.update_xaxes(showgrid=False)
        # figT.update_yaxes(showgrid=False)

        # chartS_bgn.plotly_chart(figS, use_container_width=True)
        # chartT_bgn.plotly_chart(figT, use_container_width=True)
        # summS_bgn.json({'max_bgn':round(np.max(volS_pos),3),'min_bgn':round(np.min(volS_neg),3)})
        # summT_bgn.json({'max_bgn':round(np.max(volT_pos),3),'min_bgn':round(np.min(volT_neg),3)})
    except Exception as e:
        fig = px.bar(x=[0], y=[0])
        chartR_bgn.plotly_chart(fig, use_container_width=True)
        chartS_bgn.plotly_chart(fig, use_container_width=True)
        chartT_bgn.plotly_chart(fig, use_container_width=True)
        print(e)

def estimate_coef(x, y):
    n = np.size(x)
    m_x = np.mean(x)
    m_y = np.mean(y)
    SS_xy = np.sum(y*x) - n*m_y*m_x
    SS_xx = np.sum(x*x) - n*m_x*m_x
    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1*m_x  
    return (b_0, b_1)

def form_cal(object):
    global project_cal, chartR_cal, chartS_cal, chartT_cal, summR_cal, summS_cal, summT_cal, data_json_cal

    placeholder = st.empty()
    with placeholder.container():
        col1, col2 = st.columns([1,3])
        project_cal = col1.selectbox('Project calibration', load_json(object, "project"))
        data_json_cal = col1.empty()

        tab1, tab2, tab3 = col2.tabs(["Phase R", "Phase S", "Phase T"])
        with tab1:
            chartR_cal = st.empty()
            summR_cal = st.empty()
        with tab2:
            chartS_cal = st.empty()
            summS_cal = st.empty()
        with tab3:
            chartT_cal = st.empty()
            summT_cal = st.empty()
        show_cal("calibration")

def show_cal(obj):
    idx_project = load_json(obj, "project").index(project_cal)
    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    xaxis_title = "charge (pC)"
    data_json_cal.json({
        'project': project_cal,
        'operator': json_object[obj][idx_project]["operator"],
        'hfct_model': json_object[obj][idx_project]["sensor"],
        'calibrator': json_object[obj][idx_project]["calibrator"]
    })
    try:
        volR = json_object[obj][idx_project]["volR"]
        # volS = json_object[obj][idx_project]["volS"]
        # volT = json_object[obj][idx_project]["volT"]
        xaxis = json_object[obj][idx_project]["xaxis"]
        
        figR = px.line(x=xaxis, y=volR, markers=True)
        figR.update_layout(xaxis_title=xaxis_title,yaxis_title="voltage (mV)")
        figR.update_xaxes(showgrid=False)
        figR.update_yaxes(showgrid=False)
        bR = estimate_coef(np.array(xaxis),np.array(volR))

        chartR_cal.plotly_chart(figR, use_container_width=True)
        summR_cal.json({'intercept':round(bR[0],3),'slope':round(bR[1],3)})

        # figS = px.line(x=xaxis, y=volS, markers=True)
        # figS.update_layout(xaxis_title=xaxis_title,yaxis_title="voltage (mV)")
        # figS.update_xaxes(showgrid=False)
        # figS.update_yaxes(showgrid=False)
        # bS = estimate_coef(np.array(xaxis),np.array(volS))
        
        # figT = px.line(x=xaxis, y=volT, markers=True)
        # figT.update_layout(xaxis_title=xaxis_title,yaxis_title="voltage (mV)")
        # figT.update_xaxes(showgrid=False)
        # figT.update_yaxes(showgrid=False)
        # bT = estimate_coef(np.array(xaxis),np.array(volT))

        # chartS_cal.plotly_chart(figS, use_container_width=True)
        # chartT_cal.plotly_chart(figT, use_container_width=True)
        # summS_cal.json({'intercept':round(bS[0],3),'slope':round(bS[1],3)})
        # summT_cal.json({'intercept':round(bT[0],3),'slope':round(bT[1],3)})
    except Exception as e:
        fig = px.bar(x=[0], y=[0])
        chartR_cal.plotly_chart(fig, use_container_width=True)
        chartS_cal.plotly_chart(fig, use_container_width=True)
        chartT_cal.plotly_chart(fig, use_container_width=True)
        print(e)

def form_pd(object):
    global project_pd, chartR_pd, chartS_pd, chartT_pd, summR_pd, summS_pd, summT_pd, data_json_pd

    placeholder = st.empty()
    with placeholder.container():
        col1, col2 = st.columns([1,3])
        project_pd = col1.selectbox('Project partial discharge', load_json(object, "project"))
        data_json_pd = col1.empty()

        tab1, tab2, tab3 = col2.tabs(["max-min", "number", "prpd"])
        with tab1:
            chartR_pd = st.empty()
            summR_pd = st.empty()
        with tab2:
            chartS_pd = st.empty()
            summS_pd = st.empty()
        with tab3:
            chartT_pd = st.empty()
            summT_pd = st.empty ()
        show_pd("registration")

def show_pd(object):
    idx_project = load_json(object, "project").index(project_pd)
    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    date_time = datetime.datetime.fromtimestamp(int(json_object[object][idx_project]["time"]))
 
    data_json_pd.json({
        'project': project_pd,
        'time': date_time.strftime('%Y-%m-%d %H:%M:%S'),
        'operator': json_object[object][idx_project]["operator"],
        'voltage': json_object[object][idx_project]["voltage"],
        'sensor': json_object[object][idx_project]["sensor"],
        'material': json_object[object][idx_project]["material"],
    })

def main():
    tab1, tab2, tab3 = st.tabs(["Background", "Calibration", "Acquisition"])
    with tab1:
        form_bgn("background")
    with tab2:
        form_cal("calibration")
    with tab3:
        form_pd("registration")
main()