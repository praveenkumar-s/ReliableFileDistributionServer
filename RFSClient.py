import requests
import sys
import os
import uuid
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))


class UploadFile():
    def __init__(self, targetFileorFolder , UploadAs  ):
        self.targetFileorFolder = targetFileorFolder
        self.UploadAs = UploadAs
        self.id = str(uuid.uuid1())
        self.timeout = 4000 #TODO Change as config

    def is_zip_needed(self):
        return os.path.isdir(self.targetFileorFolder)

    def createZip(self):
        zipf = zipfile.ZipFile(self.id+'.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(self.targetFileorFolder, zipf)
        zipf.close
    
    def upload(self):
        if(self.is_zip_needed):
            self.createZip()
            self.id = self.id+'.zip'
        else:
            self.id = self.targetFileorFolder
        URL = 'http://192.168.88.219:5000/upload' #TODO: Change to config 
        files = {'file': open(self.id, 'rb')}
        resp = requests.post(URL+'/'+self.UploadAs , files = files)
        if(resp.status_code == 201):
            return True
        else:
            print("Error while upload: "+ resp.text)
            return False
    

        



if __name__ == '__main__':
    choice = sys.argv[1]
    if(choice.strip().lower()=="1"):#upload        
        target = sys.argv[2]
        destination = sys.argv[3]
        upObj = UploadFile(target, destination)
        status = upObj.upload()
        print("upload status : "+ str(status))

        
    elif(choice.strip().lower()=="2"):#download
        pass
    else:
        print("Invalid Choice! ")
        raise " Invalid Choice selected "