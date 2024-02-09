import time
import json
import redis
import streamlit as st
import plotly.express as px
from multiprocessing import Process
from subprocess import Popen, PIPE, STDOUT
import asyncio
import numpy as np

json_path = 'subprocess/data.json'
process_path = 'subprocess/pro_cal.py'
r = redis.Redis(host='localhost', port=6379, db=0)

st.set_page_config(page_title="Calibration", page_icon="🦀", layout="wide")
st.markdown("# Calibration Form")

def write_json(new_data, filename=json_path):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["calibration"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def load_json(object1, object2):
    arr = []
    with open(json_path, 'r') as openfile:
        json_object = json.load(openfile)
    for project in json_object[object1]:
        options = project[object2]
        arr.append(options)
    return arr

def job():
    p = Popen(["python", process_path], stdout=PIPE, stderr=STDOUT, shell=True)
    while (event := p.stdout.readline().decode("utf-8")) != "":
        new_event = event.rstrip()
        print(new_event)
        if new_event == 'finish':
            r.set('foo', 'end')

def estimate_coef(x, y):
    n = np.size(x)
    m_x = np.mean(x)
    m_y = np.mean(y)
    SS_xy = np.sum(y*x) - n*m_y*m_x
    SS_xx = np.sum(x*x) - n*m_x*m_x
    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1*m_x
    return (b_0, b_1)

def charts(obj):
    idx_project = load_json(obj, "project").index(project)
    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    data_json.json({
        'project': project,
        'operator': json_object[obj][idx_project]["operator"],
        'hfct_model': json_object[obj][idx_project]["sensor"],
        'calibrator': json_object[obj][idx_project]["calibrator"]
    })
    try:
        xaxis = json_object[obj][idx_project]["xaxis"] 
        volR = json_object[obj][idx_project]["volR"]

        figR = px.line(x=xaxis, y=volR, markers=True)
        figR.update_layout(xaxis_title="charge (pC)",yaxis_title="voltage (mV)")
        figR.update_xaxes(showgrid=False)
        figR.update_yaxes(showgrid=False)
        chartR.plotly_chart(figR, use_container_width=True)
        if len(volR) > 1 :
            bR = estimate_coef(np.array(xaxis),np.array(volR))
            summR.json({'intercept':round(bR[0],3),'slope':round(bR[1],3)})
    except:
        figR = px.line(x=[0], y=[0])
        figR.update_layout(xaxis_title="charge (pC)",yaxis_title="voltage (mV)")
        figR.update_xaxes(showgrid=False)
        figR.update_yaxes(showgrid=False)
        chartR.plotly_chart(figR, use_container_width=True)

def new_project():
    global project,operator,sensor,iteration,calibrator
    with st.form("my_form"):
        cols = st.columns(4)
        project = cols[0].text_input('Project name')
        operator = cols[1].text_input('Operator name')
        sensor = cols[2].selectbox('HFCT model', load_json("sensor-option", "sensor"))
        calibrator = cols[3].selectbox('Calibrator model', load_json("calibrator-option", "model"))

        dictionary = {
            "time": time.time(),
            "project": project,
            "operator": operator,
            "sensor": sensor,
            "calibrator": calibrator,
            "xaxis": [],
            "volR": []
        }

        submitted = st.form_submit_button("Built project")
        if submitted:
            if project in load_json("calibration", "project"):
                st.warning('Please create different project name!', icon="⚠️")
            else:
                write_json(dictionary)
                st.success('Data saved!', icon="✅")

async def progress_async():
    old_iteration = 0
    r.delete('count')
    while True:
        try:
            new_iteration = int(r.get('count').decode())
            print(new_iteration)
            if old_iteration != new_iteration:
                status.progress(int(new_iteration/iteration*100/3))
            elif old_iteration == iteration*3:
                r.delete('count')
                status.success("Iteration done 👍")
                print("async break")
                charts("calibration")
                break
            old_iteration = new_iteration
        except Exception as e:
            print(e)
            status.info('Please wait', icon="ℹ️")
        _ = await asyncio.sleep(1)

def edit_project():
    global project,charge,iteration,chartR,summR,data_json,status
    placeholder = st.empty()
    with placeholder.container():
        col1, col2 = st.columns([1,3])
        project = col1.selectbox('Project', load_json("calibration", "project"))
        charge = col1.number_input('Charge (pC)', step=1)
        iteration = col1.slider('Iteration', 1, 10, 3)
        checkR = col1.checkbox('Channel 2 -> HFCT-R')
        start = col1.button('Start')
        status = col1.empty()
        data_json = col1.empty()

        chartR = col2.empty()
        summR = col2.empty()

        if project:
            charts("calibration")
        if start:
            if checkR:
                r.set('project', project)
                r.set('charge', charge)
                r.set('iteration', iteration)
                r.set('foo', 'start')
                p = Process(target=job, daemon=True)
                p.start()
                asyncio.run(progress_async())
            else:
                status.warning('Make sure to conenct channel', icon="⚠️")

def main():
    tab1, tab2 = st.tabs(["Create Project", "Edit Project"])
    with tab1:
        new_project()
    with tab2:
        edit_project()

main()