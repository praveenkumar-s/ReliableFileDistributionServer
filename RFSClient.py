import requests
import sys
import os
import uuid
import zipfile
import shutil
import trace
import traceback


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

def copytree(src, dst, symlinks=False):
    names = os.listdir(src)
    if(not os.path.exists(dst)):
        os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                shutil.move(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Exception as err:
            errors.extend(err.args[0])
    if errors:
        raise Exception(errors)

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
        URL = 'http://192.168.88.219:5050/upload' #TODO: Change to config 
        files = {'file': open(self.id, 'rb')}
        resp = requests.post(URL+'/'+self.UploadAs , files = files)
        if(resp.status_code == 201):
            return True
        else:
            print("Error while upload: "+ resp.text)
            return False
    

class DownloadFile():
    def __init__(self, FiletoDownload , Destination):
        self.FiletoDownload = FiletoDownload
        self.Destination = Destination
        self.id = str(uuid.uuid1())
    
    def is_Unzip_needed(self):
        if('.zip' in self.FiletoDownload.lower()):
            return True
        return False
    
    def unzip_file(self):
        with zipfile.ZipFile(self.FiletoDownload, 'r') as zip_ref:
            zip_ref.extractall(self.id)
        copytree(self.id+'/'+os.listdir(self.id)[0], self.Destination)    
        shutil.rmtree(self.id)
        
        
            

    def download(self):
        try:
            URL = 'http://192.168.88.219:5050/download/'+self.FiletoDownload
            rs = requests.get(URL)
            open(self.FiletoDownload , 'wb+').write(rs.content)
            if(self.is_Unzip_needed()):
                self.unzip_file()
            return True
        except:
            print("Error Occurred in File download "+ str(sys.exc_info()))
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
        file_to_download = sys.argv[2]
        destination = sys.argv[3]
        downObj = DownloadFile(file_to_download , destination)
        status = downObj.download()
        print("Download status : " + str(status))
    else:
        print("Invalid Choice! ")
        raise " Invalid Choice selected "