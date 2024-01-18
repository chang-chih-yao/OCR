import base64
import sys
import os
from subprocess import Popen, PIPE

def ttt():
    is_file = True
    file_or_dir = sys.argv[1]
    if file_or_dir == '-f':
        is_file = True
    elif file_or_dir == '-d':
        is_file = False
    else:
        print('bag args')
        sys.exit()
    txt_len = int(sys.argv[2])
    input_file = sys.argv[3]
    # output_file = sys.argv[4]
    
    if os.path.exists(input_file) == False:
        print(f'No such file: "{input_file}"')
        sys.exit()


    if is_file:
        proc = Popen(["xz", "-c", "-5", input_file], stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        #stdout = stdout.decode()
        encoded_data_str = base64.b64encode(stdout).decode('utf-8')
        #print(encoded_data_str)
        #stderr = stderr.decode()
        #print("Output:", stdout)
        #print("Error:", stderr)
        #exit()
    else:
        with open(input_file, 'rb') as binary_file:
            binary_data = binary_file.read()
        encoded_data_str = base64.b64encode(binary_data).decode('utf-8')
    


    #os.system('xz -k -5 ' + input_file)
    #with open(input_file + '.xz', 'rb') as binary_file:
    #    binary_data = binary_file.read()
    #os.remove(input_file + '.xz')
    #encoded_data_str = base64.b64encode(binary_data).decode('utf-8')
    
    result_str = ''
    i = 0
    while(True):
        if (i+1)*txt_len >= len(encoded_data_str):
            sub_str = encoded_data_str[i*txt_len:(i+1)*txt_len] + '\n'
            result_str += sub_str
            break
        sub_str = encoded_data_str[i*txt_len:(i+1)*txt_len] + '\n'
        result_str += sub_str
        i += 1

    #print(result_str)
    
    stdin_vim = Popen(["vim", "-R", "-u", "NONE", "-"], stdin=PIPE)
    stdin_vim.communicate(input=result_str.encode('utf-8'))

    # with open(output_file, 'w') as text_file:
    #     text_file.write(result_str)
    

