import time
import json
import redis
import streamlit as st
import plotly.express as px
import multiprocessing as mp
from subprocess import Popen, PIPE, STDOUT
import numpy as np
import asyncio

json_path = 'subprocess/data.json'
process_path = 'subprocess/pro_bgn.py'
r = redis.Redis(host='localhost', port=6379, db=0)

st.set_page_config(page_title="Background", page_icon="🐡", layout="wide")
st.markdown("# Background Form")

def write_json(new_data, filename=json_path):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["background"].append(new_data)
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

def charts(obj):
    idx_project = load_json(obj, "project").index(project)
    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    data_json.json({
        'project': project,
        'operator': json_object[obj][idx_project]["operator"],
        'hfct_model': json_object[obj][idx_project]["sensor"],
        'count': len(json_object[obj][idx_project]["xaxis"])
    })
    try:
        xaxis = np.array(json_object[obj][idx_project]["xaxis"])

        volR_pos = np.array([x for x in json_object[obj][idx_project]["volR"] if x>0])
        kind = []
        for element in volR_pos: kind.append('bgnR_pos')
        arrVolR_pos = np.concatenate((np.reshape(xaxis,(-1,1)),np.reshape(volR_pos,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

        volR_neg = np.array([x for x in json_object[obj][idx_project]["volR"] if x<=0])
        kind = []
        for element in volR_neg: kind.append('bgnR_neg')
        arrVolR_neg = np.concatenate((np.reshape(xaxis,(-1,1)),np.reshape(volR_neg,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

        arrVolR = np.vstack((arrVolR_pos,arrVolR_neg))

        figR = px.line(x=arrVolR[:,0], y=arrVolR[:,1], color=arrVolR[:,2], markers=True)
        figR.update_layout(xaxis_title="n sample",yaxis_title="voltage (mV)")
        figR.update_xaxes(showgrid=False)
        figR.update_yaxes(showgrid=False)

        chartR.plotly_chart(figR, use_container_width=True)
        summR.json({'max_bgn':round(np.max(volR_pos),3),'min_bgn':round(np.min(volR_neg),3)})

    except Exception as e:
        # print(e)
        fig = px.line(x=[0], y=[0], markers=True)
        chartR.plotly_chart(fig, use_container_width=True)

async def progress_async():
    old_iteration = 0
    r.delete('count')
    while True:
        try:
            new_iteration = int(r.get('count').decode())
            if old_iteration != new_iteration:
                status.progress(int(new_iteration/iteration*100/3))
            elif old_iteration == iteration*3:
                r.delete('count')
                status.success("Iteration done 👍")
                print("async break")
                charts("background")
                break
            old_iteration = new_iteration
        except Exception as e:
            print(e)
            status.info('Please wait', icon="ℹ️")
        _ = await asyncio.sleep(1)

def new_project():
    global project,operator,sensor,iteration,calibrator
    with st.form("my_form"):
        cols = st.columns(3)
        project = cols[0].text_input('Project name')
        operator = cols[1].text_input('Operator name')
        sensor = cols[2].selectbox('HFCT model', load_json("sensor-option", "sensor"))

        dictionary = {
            "time": time.time(),
            "project": project,
            "operator": operator,
            "sensor": sensor,
            "xaxis": [],
            "volR": []
        }

        submitted = st.form_submit_button("Built project")
        if submitted:           
            if project in load_json("background", "project"):
                st.warning('Please create different project name!', icon="⚠️")
            else:
                write_json(dictionary)
                st.success('Data saved!', icon="✅")

def edit_project():
    global project,iteration,chartR,chartS,chartT,summR,summS,summT,data_json,status
    placeholder = st.empty()
    with placeholder.container():
        col1, col2 = st.columns([1,3])
        project = col1.selectbox('Project', load_json("background", "project"))
        iteration = col1.slider('Iteration', 1, 10, 3)
        checkR = col1.checkbox('Channel 2 -> HFCT-R')
        start = col1.button('Start')
        status = col1.empty()
        data_json = col1.empty()
        
        chartR = col2.empty()
        summR = col2.empty()
         
        if project:
            charts("background")
        if start:
            if checkR:
                r.set('project', project)
                r.set('iteration', iteration)
                r.set('foo', 'start')
                p = mp.Process(target=job, daemon=True)
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