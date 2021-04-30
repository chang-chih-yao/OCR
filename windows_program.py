import psutil
import time

for i in range(10):
    for p in psutil.process_iter():
        program_name = str(p.name).split('name=')[-1].split(')')[0].split(',')[0]
        if program_name == "'XenLdr.exe'":
            #print(program_name)
            print(p.cpu_percent())
        # elif program_name == "'chrome.exe'":
        #     print(p.cpu_percent())
    print('----------------------')
    time.sleep(0.5)