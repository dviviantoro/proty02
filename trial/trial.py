from subprocess import Popen, PIPE

with Popen(["python", "bgn.py", "1023", "26.67", "kambing"], stdout=PIPE) as p:
    while True:
        text = p.stdout.read1().decode("utf-8")
        print(text, end='', flush=True)

# result = subprocess.run(["python", "my_script.py", "2", "4"], capture_output=True, text=True)
# print(result.stdout)
