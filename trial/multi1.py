import multiprocessing as mp
import numpy as np
import time


shared_values = mp.Array('d', range(2))

def heavy_pipeline_task(shared_values):
    counter = 0
    while True:
        shared_values[0] = counter
        shared_values[1] = np.sum(np.random.normal(size=(1000, 1000)))
        counter += 1


pipeline_job = mp.Process(
    target=heavy_pipeline_task,
    args=(shared_values,),
    daemon=True)
pipeline_job.start()

for i in range(1000):
    time.sleep(.4)
    print(f"pass {i}: {int(shared_values[0])}, {shared_values[1]}")