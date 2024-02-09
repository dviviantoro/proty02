# import subprocess
from subprocess import Popen, PIPE, STDOUT
import os
import signal
 
cmd = ["python", "bgn.py"]

p = Popen(["python", "bgn.py", "1023", "26.67", "kambing"], stdout=PIPE,
                  stderr=STDOUT, shell=True)
# p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
 
while (line := p.stdout.readline().decode("utf-8")) != "":
    line = line.rstrip()
    print(line)
    if line=="process=3":
        print("sampaisini")
        os.kill(p.pid, signal.CTRL_BREAK_EVENT)

        # p.terminate()
        # try:
        #     Popen.terminate()
        # except:
        print("kill failed")
        
        # break
        # p.kill()
    # if not line: break
    # if '"Progress"' in line:
    #     progress = float(line.split(":")[1].rstrip(","))
    #     print(f"Progress: {progress:.2f}")
 
# print(f"End of output.  Return code: {p.wait()}")

# while True:
#     line = p.stdout.readline().decode("utf-8")
#     print(line)
#     if not line: break
print("finish")