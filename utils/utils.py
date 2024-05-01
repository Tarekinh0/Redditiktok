import shutil

def check_if_is_already_done(md5sum):
    with open("index.txt", 'r') as file: 
        file_content = file.read() 
    if md5sum in file_content: 
        return True
    else : 
        return False
    
def erase_temp_folder():
    try:
        shutil.rmtree('./temp', ignore_errors=False, onerror=None)
    except IOError as io_err:
        print(io_err)
    