import time
import json
import datetime
import numpy as np
import plotly.express as px
from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Process
import streamlit as st
import os
import signal
import asyncio
import redis

json_path = 'subprocess/data.json'
process_path = 'subprocess/pro_act.py'
temp_json_path = 'subprocess/temp.json'

r = redis.Redis(host='localhost', port=6379, db=0)

st.set_page_config(page_title="Project", page_icon="🐢", layout="wide")
st.markdown("# Partial Discharge Form")

def write_json(new_data, filename=json_path):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["registration"].append(new_data)
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

timestamp = np.array([])
maxR = np.array([])
minR = np.array([])
nPosR = np.array([])
nNegR = np.array([])

def load_temp_json():
    global timestamp,maxR,minR,maxS,minS,maxT,minT,nPosR,nNegR,nPosS,nNegS,nPosT,nNegT,arr
    a_file = open(temp_json_path, "r")
    json_object = json.load(a_file)
    new_timestamp = json_object["iteration"][0]["time"]
    new_count = json_object["iteration"][0]["count"]
    new_maxR = json_object["iteration"][0]["maxR"]
    new_minR = json_object["iteration"][0]["minR"]
    new_nPosR = json_object["iteration"][0]["nPosR"]
    new_nNegR = json_object["iteration"][0]["nNegR"]
    new_arr = np.array(json.loads(json_object["iteration"][0]["arr"]), dtype=object)
    # new_arr = np.array(json_object["iteration"][0]["arr"], dtype=object)
    # new_arr = np.array(json.loads(json.dumps(json_object["iteration"][0]["arr"])))
    # new_arr = np.asarray(json_object["iteration"][0]["arr"], dtype=object)
    # new_arr = np.array(json_object["iteration"][0]["arr"])
    # print(new_arr)
    # print(arr)

    timestamp = np.append(timestamp, new_timestamp)
    maxR = np.append(maxR, new_maxR)
    minR = np.append(minR, new_minR)
    
    arr = np.vstack((arr, new_arr))
    fig_prpd = px.scatter(x=arr[:,0],y=arr[:,1],color=arr[:,2])
    fig_prpd.update_layout(xaxis_title="timestamp",yaxis_title="voltage")
    maxmin_pC_chart.plotly_chart(fig_prpd, use_container_width=True)

    kind = []
    for element in maxR: kind.append('maxR')
    arrMaxR = np.concatenate((np.reshape(timestamp,(-1,1)),np.reshape(maxR,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

    kind = []
    for element in minR: kind.append('minR')
    arrMinR = np.concatenate((np.reshape(timestamp,(-1,1)),np.reshape(minR,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

    arrMaxMin = np.vstack((arrMaxR,arrMinR))
    fig_maxmin = px.line(x=arrMaxMin[:,0],y=arrMaxMin[:,1],color=arrMaxMin[:,2], markers=True)
    fig_maxmin.update_layout(xaxis_title="timestamp",yaxis_title="voltage")
    maxmin_chart.plotly_chart(fig_maxmin, use_container_width=True)
    
    nPosR = np.append(nPosR, new_nPosR)
    nNegR = np.append(nNegR, new_nNegR)

    kind = []
    for element in nPosR: kind.append('nPosR')
    arrnPosR = np.concatenate((np.reshape(timestamp,(-1,1)),np.reshape(nPosR,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

    kind = []
    for element in nNegR: kind.append('nNegR')
    arrnNegR = np.concatenate((np.reshape(timestamp,(-1,1)),np.reshape(nNegR,(-1,1)),np.reshape(kind,(-1,1))), axis=1, dtype=object)

    arrn = np.concatenate((arrnPosR,arrnNegR))
    fig_number = px.line(x=arrn[:,0],y=arrn[:,1],color=arrn[:,2], markers=True)
    fig_number.update_layout(xaxis_title="timestamp",yaxis_title="number")
    number_chart.plotly_chart(fig_number, use_container_width=True)

def gen_sine():
    global arr
    amplitude = 1000
    Fs = 360
    sample = 1500
    step = 360/sample
    x = np.arange(0,360,step)
    yR = amplitude * (np.sin(2*np.pi*x/Fs))
    ysine = yR
    xsine = x
    
    ksine = []
    for element in xsine:
        ksine.append("sine")
    
    arr = np.concatenate((np.reshape(xsine, (-1,1)), np.reshape(ysine, (-1,1)), np.reshape(ksine, (-1,1))), axis=1, dtype=object)


async def draw_async():
    old_count = 0
    gen_sine()
    # load_temp_json()
    while True:
        try:
            new_count = r.get('count').decode()
            if old_count != new_count:
                load_temp_json()
            old_count = new_count
        except Exception as e:
            print(e)
            print("process getting started")

        if r.get('foo').decode() == 'end':
            r.delete('count')
            print("async break")
            break

        _ = await asyncio.sleep(3)

def new_project():
    with st.form("my_form", clear_on_submit=True):        
        cols = st.columns(5)
        project = cols[0].text_input('Project name') 
        operator = cols[1].text_input('Operator name')
        voltage = cols[2].selectbox('Working voltage',load_json("voltage-option", "voltage"))
        sensor = cols[3].selectbox('HFCT model',load_json("sensor-option", "sensor"))
        material = cols[4].selectbox('Insulation material',load_json("material-option", "material"))
        
        dictionary = {
            "time": time.time(),
            "project": project,
            "operator": operator,
            "voltage": voltage,
            "sensor": sensor,
            "material": material,
        }

        submitted = st.form_submit_button("Built project")
        if submitted:
            if project in load_json("registration", "project"):
                st.warning('Please create different project name!', icon="⚠️")
            else:
                write_json(dictionary)
                st.success('Data saved!', icon="✅")

def load_data_json(object):
    idx_project = load_json(object, "project").index(project)
    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    date_time = datetime.datetime.fromtimestamp(int(json_object[object][idx_project]["time"]))
    data_json.json({
        'project': project,
        'time': date_time.strftime('%Y-%m-%d %H:%M:%S'),
        'operator': json_object[object][idx_project]["operator"],
        'voltage': json_object[object][idx_project]["voltage"],
        'sensor': json_object[object][idx_project]["sensor"],
        'material': json_object[object][idx_project]["material"],
    })

def edit_project():
    global project,bgn,src,maxmin_pC_chart,maxmin_chart,number_chart,data_json
    placeholder = st.empty()

    with placeholder.container():
        col1, col2 = st.columns([1,3])
        project = col1.selectbox('Project',load_json("registration", "project"))
        bgn = col1.selectbox('Background',load_json("background", "project"))
        cal = col1.selectbox('Calibration',load_json("calibration", "project"))
        src = col1.selectbox('Source connect to', load_json("ch1-option", "ch1")) 
        start = col1.button('Start')
        stop = col1.button('Stop')
        data_json = col1.empty()

        tab1, tab2, tab3= col2.tabs(["max-min (mV)", "max-min (pC)", "number"])
        with tab1:
            maxmin_chart = st.empty()
        with tab2:
            maxmin_pC_chart = st.empty()
        with tab3:
            number_chart = st.empty()

        if 'key' not in st.session_state:
            st.session_state.key = 0

        if stop:
            load_data_json("registration")
            r.set('foo', 'end')
            os.kill(st.session_state.key, signal.SIGABRT)
            print("end project {} at: ".format(project), st.session_state.key)
        elif start:
            load_data_json("registration")
            r.set('project', project)
            r.set('bgn', bgn)
            r.set('cal', cal)
            r.set('src', src)
            r.set('foo', 'start')
            p = Process(target=job, daemon=True)
            p.start()
            st.session_state.key = p.pid
            print("start project {} at: ".format(project), st.session_state.key) 
            asyncio.run(draw_async())
        
        if project:
            load_data_json("registration")


def main():
    tab1, tab2 = st.tabs(["Create Project", "Edit Project"])
    with tab1:
        new_project()
    with tab2:
        edit_project()


main()