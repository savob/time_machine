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
    picture_files.sort()
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
    params_read = 0 # bitwise log of keywords found to verify we had a full and correct read
    # print('Reading config from ' + config_file)

    try:
        with open(config_file, 'r') as finp:
            print(datetime.datetime.now(), 'Reading configuration file')
            for line in finp:
                if line.startswith('DELAY='):
                    x = float(line[6:])
                    x = max(1.,x)
                    x = min(60.,x) # limit 1..60
                    result[1] = x
                    params_read = params_read | 1
                if line.startswith('PATH='):
                    result[2] = line[5:-1] # strip off new line at end
                    params_read = params_read | 2
    except:
        pass

    # print('Read configuration file results ', result)
    if (params_read == 3):
        result[0] = True # read file properly, all bits set
    return result

def run_photo_frame(params):

    config_file_name    = params[0]
    delay               = params[1]
    photo_folder        = params[2]

    # Force screen to remain on and not blank
    IS_WINDOWS = sys.platform.startswith('win') # 'win32' or 'linux2' or 'linux'
    if not IS_WINDOWS:
        os.system("xset dpms force on")
        os.system("xset s off")

    # Initialize a CV2 frame to cover the entire screen
    cv2_frame = 'frame'
    cv2.namedWindow(cv2_frame, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(cv2_frame, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Find out what size of display we're working with, handle potential non-sense
    tmp = cv2.getWindowImageRect(cv2_frame)
    window_width = float(tmp[2])
    window_height = float(tmp[3])
    if window_height < 480.0 or window_width < 640.0:
        window_height = 1080.0
        window_width = 1920.0
    #print(window_height, window_height)
    
    # Scan the photo folder for a list of picture files
    picture_file_list = scan_for_files(photo_folder)
    print(datetime.datetime.now(), 'Scan found', len(picture_file_list), 'files')

    current_index   = 0     # Photo index to use
    done            = False
    last_hour       = -1    # Force a reset on first iteration (for code testing)
    
    while not done:

        # Hourly reconfiguration
        current_hour = datetime.datetime.now().hour       
        if current_hour is not last_hour:
            last_hour = current_hour

            result = check_for_config_file(config_file_name, delay, photo_folder)
            if result[0] == True:
                delay = result[1]
                photo_folder = result[2]
            
            picture_file_list = scan_for_files(photo_folder)
            print(datetime.datetime.now(), 'Scan found', len(picture_file_list), 'files')

        # Select new photo
        current_index = current_index + 1 # Just increment for now
        if current_index >= len(picture_file_list):
            current_index = 0 
        file_name = picture_file_list[current_index]

        got_image=False
        try:
            # print('Showing', file_name)
            image = cv2.imread(file_name, 1)
            if len(image) > 0:
                got_image = True
        except:
            got_image = False
        if not got_image:
            continue

        # Extract time stamps to potentially send to the displays
        date_and_time = os.path.basename(file_name)
        date_stamp = int(date_and_time[0:8])
        time_stamp = int(date_and_time[9:15])

        #-- now, maybe resize image so it shows up well without changing the aspect ratio
        #   add a border if the aspect ratio is different than the screen
        # so we upscale or downscale so it maxes out either the
        # horizontal or vertical portion of the screen
        # then add a border around it to make sure any left-over
        # parts of the screen are blacked out
        width_ratio = window_width / image.shape[1]
        height_ratio = window_height / image.shape[0]
        ratio = min(width_ratio,height_ratio)
        dimensions = (int(ratio * image.shape[1]), int(ratio * image.shape[0]))
        #print(fn, img.shape, ratio, dims[1], dims[0])
        imgresized = cv2.resize(image, dimensions, interpolation = cv2.INTER_AREA)
        #print(imgresized.shape)
        # now, one dimension (width or height) will be same as screen dim
        # and the other may be smaller than the screen dim.
        # we're going to use cv.copyMakeBorder to add a border so we
        # end up with an image that is exactly screen sized
        width_border = max(1, int((window_width-imgresized.shape[1]) / 2))
        height_border = max(1, int((window_height-imgresized.shape[0]) / 2))
        #print(hgtborder,widborder)
        bordered_image = cv2.copyMakeBorder(imgresized, height_border, height_border, width_border, width_border, cv2.BORDER_CONSTANT)
        #print('resized,bordered', imgbordered.shape)

        # Show final image while waiting for a key to potentially be pressed for exit
        cv2.imshow(cv2_frame, bordered_image)
        k = cv2.waitKey(int(delay * 1000)) & 0xff

        if k != 255: # Any key pressed
            done = True
            break
  
    # Once the photo display session ends clean up the full-frame window
    cv2.destroyWindow(cv2_frame)


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
        run_photo_frame(params)