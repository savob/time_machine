import os
import datetime
import cv2 # opencv - pip3 install opencv-python
import random
import sys
import time

#-------------------------------------------------------------
# Scan a folder tree (recursively) for jpg or png files
def scan_for_files(folder):
    picture_files=[]
    itr = os.scandir(folder)
    for entry in itr:
        if entry.is_file():
            file_name = entry.name.lower()
            if file_name.endswith('.jpg') or file_name.endswith('.png'):
                picture_files.append(entry.path)
        if entry.is_dir(): # recurse for sub-folders
            x = scan_for_files(entry.path)
            picture_files.extend(x)
    #itr.close()
    return picture_files

def check_for_config_file(config_file, def_delay, def_photo_folder):
    #
    #   Sample control file has four lines in KEY=VALUE format
    #   - delay in seconds
    #   - path to find picures and control file
    #   
    #   File is deposited into the top folder where the picures are stored (PATH)
    #   File is named instructions.ini
    #   
    #   Control file will be read hourly
    #   
    #DELAY=3.5
    #PATH=/media/pi/photoframe
    #

    result = [False, def_delay, def_photo_folder]
    readparams = 0 # bitwise log of keywords found to verify we had a full and correct read
    # print('Reading config from ' + config_file)

    try:
        with open(config_file,'r') as finp:
            print(datetime.datetime.now(), 'Reading configuration file')
            for line in finp:
                print(line)
                if line.startswith('DELAY='):
                    x = float(line[6:])
                    x = max(1.,x)
                    x = min(60.,x) # limit 1..60
                    result[1] = x
                    readparams = readparams | 1
                if line.startswith('PATH='):
                    result[2] = line[5:-1] # strip off new line at end
                    readparams = readparams | 2
    except:
        pass

    print('Read configuration file results ',result)
    if (readparams == 3):
        result[0] = True # read file properly, all bits set
    return result

# def run_photo_frame(params):

    # grab our parameters that control operation of the
    configfn    = params[0]   # name of config file to look for in top level folder 
    delay       = params[1]   # delay in seconds to show each picture
    photoFolder = params[2]   # be real careful when changing this in config file
    
    # determine if this is a windows OS based system
    IS_WINDOWS = sys.platform.startswith('win') # 'win32' or 'linux2' or 'linux'

    # initialize a CV2 frame to cover the entire screen
    cv2frame = 'frame'
    cv2.namedWindow(cv2frame, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(cv2frame, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # let's find out what size of display we're working with    
    tmp = cv2.getWindowImageRect(cv2frame)
    wid = float(tmp[2])
    hgt = float(tmp[3])
    # sometimes the getWindowImageRect returns nonsense like
    # width or height of -1 or some other non useful value
    if hgt<480.0 or wid<640.0:
        hgt=1080.0 # assume a 9h x 16w form factor
        wid=1920.0
    #print(hgt,wid)
    
    # scan the photoFolder for a list of picture files
    pictureFiles=scan_for_files(photoFolder)
    # Sort them by name (date)
    print(datetime.datetime.now(), 'Scan found', len(pictureFiles), 'files')

    # initialize for hourly and sleep processing    
    done=False
    
    # and loop forever (until some key is hit)
    while not done:
        
        # during waking hours, display pictures
        # during sleeping hours, keep display blanked
        for fn in pictureFiles:

            # let's see if it's time to do hourly tasks
            now=datetime.datetime.now()
            hour=now.hour
            if not IS_WINDOWS:
                os.system("xset dpms force on")

            #-- hourly tasks, only done when not sleeping            
            if hour!=lastHour and not sleeping:
                lastHour=hour
                if not IS_WINDOWS:
                    os.system("xset s off") # screen blanking off
                # try to read configuration file instructions.ini
                controlFn=os.path.join(photoFolder,configfn)
                result=check_for_config_file(controlFn,delay,wakehour,bedtimehour,photoFolder)
                if result[4]: # set to true for successful config file read
                    delay=result[0]
                    wakehour=result[1]
                    bedtimehour=result[2]
                    photoFolder=result[3]
                # rescan folder
                pictureFiles=scanForFiles(photoFolder)
                random.shuffle(pictureFiles)
                print(datetime.datetime.now(),'Scan found',len(pictureFiles),'files')

            #--- run always, do wake up tasks or sleep tasks
            #
            # for example wakehour might be 9am and bedtimehour might be 9pm
            # wakehour=9 and bedtimehour=21 (12+9)
            if hour>=wakehour and hour<bedtimehour:
                # we are in wake up time of day

                #--- if we were sleeping, then it is time to wake up
                if sleeping:
                    print(datetime.datetime.now(),'Wake up')
                    if not IS_WINDOWS:
                        os.system("xset s off") # screen blanking off
                        os.system("xset dpms force on")
                    sleeping=False

                #--- display a photo
                # handle fault in loading a picture
                gotImg=False
                try:
                    print('loading',fn)
                    img = cv2.imread(fn, 1)
                    if len(img)>0:
                        gotImg=True
                except:
                    gotImg=False
                if not gotImg:
                    continue
    
                #-- now, maybe resize image so it shows up well without changing the aspect ratio
                #   add a border if the aspect ratio is different than the screen
                # so we upscale or downscale so it maxes out either the
                # horizontal or vertical portion of the screen
                # then add a border around it to make sure any left-over
                # parts of the screen are blacked out
                widratio=wid/img.shape[1]
                hgtratio=hgt/img.shape[0]
                ratio=min(widratio,hgtratio)
                dims=(int(ratio*img.shape[1]),int(ratio*img.shape[0]))
                #print(fn,img.shape,ratio,dims[1],dims[0])
                imgresized=cv2.resize(img,dims,interpolation = cv2.INTER_AREA)
                #print(imgresized.shape)
                # now, one dimension (width or height) will be same as screen dim
                # and the other may be smaller than the screen dim.
                # we're going to use cv.copyMakeBorder to add a border so we
                # end up with an image that is exactly screen sized
                widborder=max(1,int((wid-imgresized.shape[1])/2))
                hgtborder=max(1,int((hgt-imgresized.shape[0])/2))
                #print(hgtborder,widborder)
                imgbordered=cv2.copyMakeBorder(imgresized,hgtborder,hgtborder,widborder,widborder,cv2.BORDER_CONSTANT)
                #print('resized,bordered',imgbordered.shape)

                # and now show the image that has been resized and bordered
                cv2.imshow(cv2frame, imgbordered)
                #--- now we pause while the photo is displayed, we do this
                #    by waiting for a key stroke.
                k = cv2.waitKey(int(delay*1000)) & 0xff
                # 255 if no key pressed (-1) or ascii-key-code (13=CR, 27=esc, 65=A, 32=spacebar)
                if k!=0xff:
                    # if a key was pressed, exit the photo frame program
                    done=True
                    break  
            else:
                sleeping=True
                k = cv2.waitKey(300*1000) & 0xff # wait 300 seconds
                # 255 if no key pressed (-1) or ascii-key-code (13=CR, 27=esc, 65=A, 32=spacebar)
                if k!=0xff:
                    done=True
  
    # when the photo display session ends, 
    # we need to clean up the cv2 full-frame window
    cv2.destroyWindow(cv2frame)



if __name__ == "__main__":

    photo_folder = '.' + os.sep + 'time_machine_photos' # top level folder for pictures
    delay_s = 4                     # seconds for each displayed picture

    print("---- Time Machine - Starting ----")

    successful_config_read = False
    config_file_name = "config_time_machine.ini" # default name to look for hourly in top level folder
    
    # search arg list for
    if len(sys.argv)>1:
        config_file_name=sys.argv[1]

    print("Reading config file: ", config_file_name)

    result = check_for_config_file(config_file_name, delay_s, photo_folder)
    if result[0] == True: # Check for successfull read of config file
        delay_s = result[1]
        photo_folder = result[2]
        successful_config_read = True
        print("Config file read: ", delay_s, photo_folder)

    time.sleep(3) # wait just a bit to read messages if any

    if not successful_config_read:
        print("\n--- Unable to read config file, terminating ---\n")
        exit()
    else:
        # and then, let's get this show on the road
        params=[config_file_name, delay_s, photo_folder]
        # run_photo_frame(params)