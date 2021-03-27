from flask import Flask , request , send_from_directory
import time
import os
import shutil
import socket

app = Flask(__name__)


UPLOAD_BUSY={}
DOWNLOAD_BUSY={}

class SafelyOperate():
    def __init__(self, file_name, wait = 30 ):
        self.file_name = file_name
        self.wait = wait

    def moveFromTempToData(self):
        tmr = 0.0 
        while tmr<self.wait:
            if(self.isBusy(self.file_name , 'down')):
                print("resource locked {0}, waiting for release".format(self.file_name))
                time.sleep(0.2)
                tmr = tmr+0.2
            else:
                UPLOAD_BUSY[self.file_name]= True
                shutil.move(os.path.join('TEMP', self.file_name), os.path.join('DATA', self.file_name))
                UPLOAD_BUSY[self.file_name]= False
                break
        return tmr

    def isBusy(self, file_name, mode ):
        try:
            if(mode=='up'):
                return UPLOAD_BUSY[file_name]
            elif(mode=='down'):
                return DOWNLOAD_BUSY[file_name]
            raise "Ivalid Mode Specified"
        except:
            return False       


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/upload/<file_name>', methods = ['POST'])
def upload(file_name):
    print("Recieved upload Request for "+ file_name)
    f = request.files['file']
    f.save('TEMP/'+file_name)
    print("Moved {0} to temp".format(file_name))
    safeHandle = SafelyOperate(file_name)
    time_Taken = safeHandle.moveFromTempToData()
    print("time taken for processing: " + str(time_Taken)) #TODO Remove 
    return 'done',201



@app.route('/download/<file_name>')
def download(file_name):
    #if file is not there in the folder , return 404
    if(not os.path.exists("DATA/"+file_name)):
        return "file: {0} not found! ".format(file_name),404
    try:
        DOWNLOAD_BUSY[file_name]=True
        print("Download Busy Flag Set "+ file_name)
        return send_from_directory(directory='DATA', filename=file_name)
    finally:
        DOWNLOAD_BUSY[file_name]=False
        print("Download Busy Flag Cleared "+ file_name)

@app.teardown_request
def checkin_db(exc):
    try:
        print "Removing db session."        
    except AttributeError:
        pass

if __name__ == '__main__':
    if(not os.path.exists('DATA')):
        os.mkdir('DATA')
    if(not os.path.exists('TEMP')):
        os.mkdir('TEMP')
    app.run(threaded=True, host= socket.gethostname() ,port = 5050)