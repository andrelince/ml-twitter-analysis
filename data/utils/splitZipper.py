import time,os,shutil
from zipfile import ZipFile

readsize = 1024
bytes = 99000000
chunksize = int(bytes)

def zip_file(unzipped_filename, zipped_filename):
    ZipFile(zipped_filename, 'w').write(unzipped_filename)

def unzip_file(zipped_filename,unzip_directory):
    with ZipFile(zipped_filename, "r") as z:
        z.extractall(unzip_directory)




def split(fromfile, todir, chunksize=chunksize, zip=False, remove_file=True):
    print("Splitting file: " + fromfile)
    if not os.path.exists(todir):  # caller handles errors
        os.mkdir(todir)
    '''else:
        for fname in os.listdir(todir):  # delete any existing files
            os.remove(os.path.join(todir, fname))'''
    partnum = 0
    input = open(fromfile, 'rb')  # use binary mode on Windows
    while 1:  # eof=empty string from read
        chunk = input.read(chunksize)  # get next part <= chunksize
        if not chunk: break
        partnum = partnum + 1
        filename = os.path.join(todir, ('database%04d' % partnum))
        fileobj = open(filename, 'wb')
        fileobj.write(chunk)
        fileobj.close()  # or simply open(  ).write(  )
        if zip:
            zip_file(filename, filename + '.zip')
            os.remove(filename)
    input.close()
    assert partnum <= 9999  # join sort fails if 5 digits
    if remove_file:
        os.remove(fromfile)
    return partnum



def join(fromdir, tofile, zip=False, remove_dir = True):
    print("Joining into file: " + tofile)
    output = open(tofile, 'wb')
    parts  = os.listdir(fromdir)
    parts.sort(  )
    if zip:
        for filename in parts:
            filepath = os.path.join(fromdir, filename)
            unzip_file(zipped_filename=filepath, unzip_directory='.')
            os.remove(filepath)
    parts = os.listdir(fromdir)
    parts.sort()
    for filename in parts:
        filepath = os.path.join(fromdir, filename)
        fileobj  = open(filepath, 'rb')
        while 1:
            filebytes = fileobj.read(readsize)
            if not filebytes: break
            output.write(filebytes)
        fileobj.close()
    output.close()
    if remove_dir:
        shutil.rmtree(fromdir)

#split(fromfile='database.sqlite',todir='database',zip=True)
#time.sleep(10)
#join(fromdir='database', tofile='database.sqlite', zip=True)

