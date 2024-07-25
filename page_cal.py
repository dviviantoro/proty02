from nicegui import ui
import os
import random
from datetime import datetime
from nicegui.events import ValueChangeEventArguments
from manipulate_json import *

fig = {
    'data': [
        {
            'type': 'scatter',
            'name': 'Trace 1',
            'x': [1, 2, 3, 4],
            'y': [1, 2, 3, 2.5],
        },
        # {
        #     'type': 'scatter',
        #     'name': 'Trace 2',
        #     'x': [1, 2, 3, 4],
        #     'y': [1.4, 1.8, 3.8, 3.2],
        #     'line': {'dash': 'dot', 'width': 3},
        # },
    ],
    'layout': {
        'margin': {'l': 15, 'r': 0, 't': 0, 'b': 15},
        'plot_bgcolor': '#E5ECF6',
        'xaxis': {'gridcolor': 'white'},
        'yaxis': {'gridcolor': 'white'},
    },
}

def add_trace():
    fig = {
        'data': [
            {
                'type': 'scatter',
                'name': 'Trace 1',
                'x': [1, 2, 3, 4],
                'y': [1, 2, 3, 2.5],
            },
            {
                'type': 'scatter',
                'name': 'Trace 2',
                'x': [1, 2, 3, 4, 20],
                'y': [1.4, 1.8, 3.8, 3.2, 20],
                'line': {'dash': 'dot', 'width': 3},
            },
            # {
            #     'type': 'scatter',
            #     'name': 'Trace 3',
            #     'x': [10, 20, 3, 4],
            #     'y': [10, 20, 3, 2.5],
            # }
        ],
        'layout': {
            'margin': {'l': 15, 'r': 0, 't': 0, 'b': 15},
            'plot_bgcolor': '#E5ECF6',
            'xaxis': {'gridcolor': 'white'},
            'yaxis': {'gridcolor': 'white'},
        },
    }
    plot_reg.update_figure(fig)

def submit_add():
    with ui.dialog() as unproper_form, ui.card():
        with ui.row():
            ui.icon('error', color='primary').classes('text-5xl w-full justify-center row')
            ui.label('Please fill properly').classes('text-base w-full justify-center row')
        ui.button('Got it', on_click= unproper_form.close).classes('w-full')
    # if ((add_charge.value).isnumeric() and (add_loop.value).isnumeric() and check_project_value and check_operator_value and check_device_value and check_sensor_value):
    #     dialog_add.close()
    #     dialog_scope.open()
    # else:
    #     unproper_form.open()
    dialog_scope.open()

def check_change_project(event: ValueChangeEventArguments):
    global check_project_value
    name = type(event.sender).__name__
    ui.notify(f'{name}: {event.value}')
    check_project_value = event.value

def check_change_operator(event: ValueChangeEventArguments):
    global check_operator_value
    name = type(event.sender).__name__
    ui.notify(f'{name}: {event.value}')
    check_operator_value = event.value

def check_change_device(event: ValueChangeEventArguments):
    global check_device_value
    name = type(event.sender).__name__
    ui.notify(f'{name}: {event.value}')
    check_device_value = event.value

def check_change_sensor(event: ValueChangeEventArguments):
    global check_sensor_value
    name = type(event.sender).__name__
    ui.notify(f'{name}: {event.value}')
    check_sensor_value = event.value

with ui.dialog() as dialog_scope:
    ui.card().classes('w-[2000px] h-[200px]')
    # with ui.row().classes('grid grid-cols-12 w-full gap-4'):
    #     with ui.column().classes('col-span-8'):
    #         plot_scope = ui.plotly(fig).classes('w-[400px] h-[400px]')
        # plot_reg = ui.plotly(fig).classes('w-full h-[300px]')

with ui.dialog() as dialog_add, ui.card():
    with ui.row():
        ui.icon('square_foot', color='primary').classes('text-6xl w-full justify-center row')
        ui.label('Input value').classes('text-3xl w-full justify-center row')
    add_charge = ui.input('Input charge (pC)').props('clearable outlined dense').classes('w-full')
    add_loop = ui.input('Input loop (n)').props('clearable outlined dense').classes('w-full')
    ui.checkbox('Check Project', on_change=check_change_project).classes('col-start-3 col-span-2')
    ui.checkbox('Check Operator', on_change=check_change_operator).classes('col-span-2')
    ui.checkbox('Check Device', on_change=check_change_device).classes('col-span-2')
    ui.checkbox('Check Sensor', on_change=check_change_sensor).classes('col-span-2')
    # ui.checkbox(display_text, on_change=lambda e, f=f: checkbox_handler(e, f)).tooltip(f)
    ui.button('Submit', on_click=lambda: submit_add()).classes('w-full')
                    

def add():
    current_dateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # load_json()
    # table.add_rows({
    #     'id': 1,
    #     'created': current_dateTime,
    #     'charge': random.randint(0, 100),
    #     'voltage': random.randint(1000, 10000)
    #     })

    q, v = get_xy(0)
    for i in len(q):
        table.add_rows({
            'id': i,
            'charge': q[i],
            'voltage': v[i]
            })

    
def remove():
    for i in range(len(table.selected)):
        table.remove_rows(table.selected[0])

columns = [
    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'left'},
    # {'name': 'created', 'label': 'Created', 'field': 'created', 'sortable': True},
    {'name': 'charge', 'label': 'Q', 'field': 'charge', 'sortable': True, 'align': 'left'},
    {'name': 'voltage', 'label': 'V', 'field': 'voltage', 'sortable': True, 'align': 'left'},
]

with ui.row().classes('grid grid-cols-12 w-full gap-4'):
    with ui.column().classes('col-span-8'), ui.card().classes('w-full h-[900px]'):
        plot_reg = ui.plotly(fig).classes('w-full h-[300px]')
        # log_cal_chart = ui.log(max_lines=10).classes('w-full h-20')
        # with ui.dropdown_button('Open me!', auto_close=True):
        with ui.expansion('Expand!', caption='Detailed raw data').classes('w-full'):
            ui.card().classes('w-full h-[100px]')
            # ui.item('Item 1', on_click=lambda: ui.notify('You clicked item 1'))
        # show number dot
        # show linear regression formula
        # show pC/volt
        plot_reg = ui.plotly(fig).classes('w-full h-[300px]')
        log_capture_chart = ui.log(max_lines=10).classes('w-full h-20')
        # show label: last scoping
        # show recent number of loop
        # show total number of loop
        # show vnserted value of volt
        # show pC/volt mean
    with ui.column().classes('col-span-4'), ui.card().classes('w-full h-[550px]'):
        with ui.scroll_area().classes('h-[530px]'):
            table = ui.table(columns=columns, rows=[], row_key='created', selection='multiple', on_select=lambda: print(table.selected)).classes('w-full')
        with ui.row():
            add_data = ui.button('Try add data', on_click=add)
            add_data = ui.button('Add data', icon='add_circle',on_click=dialog_add.open)
            del_data = ui.button('Delete data', icon='delete',on_click=remove)

ui.button('Add trace', on_click=add_trace)


# with ui.dialog() as dialog_add:
#     with ui.element('div').classes('grid grid-cols-12 w-full gap-4 col-start-3 col-span-8'):
#         with ui.element('div').classes('col-start-2 col-span-10'), ui.card():
#                 # with ui.element('p').classes('text-center font-heading text-5xl'):
#                 #     ui.label('Are you sure?')
#                 # ui.html('This is <strong>HTML</strong>.').classes('text-center font-heading text-5xl')
#                 with ui.row():
#                     ui.label('Are you sure?').classes('flex text-center font-heading text-5xl justify-center')

#                 with ui.row():
#                     with ui.element('div').classes('grid grid-cols-12 w-full gap-4 col-start-3 col-span-8'):
#                         with ui.element('div').classes('col-start-2 col-span-10'):
#                             add_charge = ui.input('Input charge (pC)').props('clearable outlined dense').classes('w-full')
#                             add_loop = ui.input('Input loop (n)').props('clearable outlined dense').classes('w-full')
#                     # ui.button('clickme', on_click=lambda: print((add_charge.value).isnumeric()))
#                     with ui.element('span').classes('col item-center justify-center row'):
#                         ui.button('clickme', on_click=lambda: submit_add())






ui.run()