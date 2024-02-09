import sys
from time import sleep
my_input = sys.argv

# def sum_two_values(a=float(my_input[1]), b=float(my_input[2])):
#     return a + b

count = 0
while True:
    count = count+1
    # print(sum_two_values())
    # sleep(1)
    # print(my_input[3])
    sleep(1)
    # print(count)

    print("process",end="=")
    print(count,flush=True)
    if count == 5:
        break

# if __name__=="__main__":
