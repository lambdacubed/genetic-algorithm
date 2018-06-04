"""
This module opens up the specific data acquisition hardware and returns the desired output

Functions:
ic() -- Grabs an image from an IC camera
NI_DAQ_voltage() -- acquires a voltage from the NI hardware (usually connected to the lock-in amplifier)

"""

import figure_of_merit_functions as figure_of_merit_f

import numpy as np  # useful general python library
import file_functions as file_f     # use this for reading and writing to files
import os   # this gives information about the current working directory

# These libraries are needed for IC cameras
from pyicic.IC_ImagingControl import *
import copy

# This is needed for the NI DAQ
import win32com.client  # Python ActiveX Client for calling and running LabVIEW

# this is needed for the picoscope
from picoscope import ps2000a

# These libraries are needed for the Andor camera
import ctypes   # this is used for being a wrapper to the c functions in the Andor dll
import time     # this is used to make the program sleep for a little bit so the camera calibrates fully
import matplotlib.pyplot as plt
import matplotlib.cm as cm

DAQ_DEVICES = ("Andor", "NI_DAQ", "IC", "Picoscope")

# These are Andor error codes which are given in the sdk pdf file
DRV_SUCCESS = 20002
DRV_IDLE = 20073

# Pixel formats for imaging source cameras as strings which organize pixels top down instead of down up
PIXEL_FORMAT_TOP_DOWN = ('Y800', 'YGB0', 'YGB1', 'UYBY', 'Y16')

class data_acqusition(object):
    """This object is used to initialize, acquire data from, and shut down various different hardware for data acquisition
    """
    
    def __init__(self, device, fom_num):
        self.device = device    # save which acquisition device is being used
        initialize_array = file_f.read_initialization_variables("\\"+ self.device + "\\" + self.device + " properties.ini") # read in the initialization information from the file at device/device properites.ini
        self.fom_num = fom_num
        # initialize the specific device being called
        if (device == DAQ_DEVICES[0]):  # if the device name is "Andor"
            self.__initialize_andor(initialize_array)
        elif (device == DAQ_DEVICES[1]):    # if the device name is "NI_DAQ"
            self.__initialize_NI_DAQ(initialize_array)
        elif (device == DAQ_DEVICES[2]):    # if the device name is "IC"
            self.__initialize_IC(initialize_array)
        elif (device == DAQ_DEVICES[3]):    # if the device name is "Picoscope"
            self.__initialize_pico(initialize_array)
        else:
            print("Error: The device you entered into data acquisition wasn't valid")
            print("The possible devices are: ", DAQ_DEVICES)
            exit()


    def __check_success(self, error_value, function_name):
        """Check whether or not the program was able to perform the given function for the Andor camera
        
        Parameters
        ----------
        error_value : error value, int
            This is the error value returned from any Andor function
        function_name : function name, string
            This is a string which denotes which function returned this error value
        """
        if (error_value != DRV_SUCCESS):    # if the error value wasn't success
            print("Andor", function_name,"Error", error_value)
            exit()

    def __initialize_andor(self, initialize_array):
        """Initialize the Andor camera to be ready to capture images

        Parameters
        ----------
        initialize_array : initialization array, numpy array
            This contains information from the "Andor/Andor properties.ini" file about what Andor properties to use for image capture
        """

        # get the information from the .ini file 
        read_mode_top = int(initialize_array[0])    # readout mode options: 0 Full Vertical binning;    1 Multi-Track;  2 Random-Track;  3 Single-Track;    4 Image;
        acquisition_mode_top = int(initialize_array[1])     # acquisition mode options: 1 Single scan;  2 Accumulate;   3 Kinetics;  4 Fast Kinetics;   5 Run till abort;
        exposure_time_top = float(initialize_array[2])      # time in seconds
        trigger_mode_top = int(initialize_array[3])     # trigger mode options: 0 internal; 1 external; 6 external start;   7 external exposure (bulb); 9 external FVB EM;  10 software trigger;    12 external charge shifting;
        horizontal_binning_top = int(initialize_array[4])   # set the horizontal binning
        vertical_binning_top = int(initialize_array[5])     # set the vertical binning
        horizontal_start_top = int(initialize_array[6])     # set the horizontal start pixel of the subregion of the camera which to take a picture from
        horizontal_end_top = int(initialize_array[7])       # set the horizontal end pixel
        vertical_start_top = int(initialize_array[8])   # set the vertical start pixel
        vertical_end_top = int(initialize_array[9])     # set the vertical end pixel
        
        
        # Load the atmcd64.dll file 
        directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
        self.andor_dll = ctypes.windll.LoadLibrary(directory_path + '\\Andor\\atmcd32d.dll')  # load the andor dll from the directory Andor/
        
        
        # Initialize camera
        aBuffer = ctypes.c_char_p()     # The buffer tells the initialize function where the driver files are. Currently, they're in the same folder as this .py file
        error_value = self.andor_dll.Initialize(aBuffer)
        self.__check_success(error_value, "Initialize")
        
        
        # Determine size (in pixels of camera)
        gblXPixels = ctypes.c_int()     # Total number of horizontal pixels
        gblYPixels = ctypes.c_int()     # Total number of vertical pixels
        error_value = self.andor_dll.GetDetector(ctypes.byref(gblXPixels),ctypes.byref(gblYPixels))
        self.__check_success(error_value,"GetDetector")
        
        # Set vertical shift speed to recommended value
        vertical_shift_index = ctypes.c_int()   # the index to access specific vertical shift speeds 
        vertical_speed = ctypes.c_float()   # speed of the vertical speed shift in microseconds per pixel shift
        error_value = self.andor_dll.GetFastestRecommendedVSSpeed(ctypes.byref(vertical_shift_index),ctypes.byref(vertical_speed))
        self.__check_success(error_value,"Get Fastest Recommended Vertical Shift Speed")
        error_value = self.andor_dll.SetVSSpeed(vertical_shift_index)
        self.__check_success(error_value,"Set Vertical Shift Speed")
        
        
        # Set horizontal shift speed to the maximum
        horizontal_shift_index = ctypes.c_int(0)        # the index to access specific horizontal shift speeds
        AD_converter_index = ctypes.c_int()             # the specific index to access a given A-D converter
        number_AD = ctypes.c_int(0)                     # the number of A-D converters in the camera
        number_speeds = ctypes.c_int()                  # number of speeds available
        horizontal_speed = ctypes.c_float()             # horizontal shift speed
        max_horizontal_speed = ctypes.c_float(0)        # maximum horizontal speed
        error_value = self.andor_dll.GetNumberADChannels(ctypes.byref(number_AD))
        self.__check_success(error_value,"Get Number AD Channels")
        for each_AD in range(number_AD.value):
            error_value = self.andor_dll.GetNumberHSSpeeds(AD_converter_index, ctypes.c_int(0), ctypes.byref(number_speeds))
            self.__check_success(error_value, "Get Number Horizontal Shift Speeds")
            for each_speed_index in range(number_speeds.value):
                error_value = self.andor_dll.GetHSSpeed(ctypes.c_int(each_AD),ctypes.c_int(0),ctypes.c_int(each_speed_index),ctypes.byref(horizontal_speed))
                self.__check_success(error_value,"Get Horizontal Shift Speed")
                if (horizontal_speed.value > max_horizontal_speed.value):
                    max_horizontal_speed.value = horizontal_speed.value
                    horizontal_shift_index = ctypes.c_int(each_speed_index)
                    AD_converter_index = ctypes.c_int(each_AD)
        error_value = self.andor_dll.SetADChannel(AD_converter_index)
        self.__check_success(error_value,"Set AD Channel")
        error_value = self.andor_dll.SetHSSpeed(ctypes.c_int(0), horizontal_shift_index)
        self.__check_success(error_value, "Set Horizontal Speed Index")
        
        # Turn the camera cooler on
        error_value = self.andor_dll.CoolerON()
        self.__check_success(error_value,"Turn Cooler On")
        
        
        # Check to make sure cooler is on
        cooler_on = ctypes.c_int()
        error_value = self.andor_dll.IsCoolerOn(ctypes.byref(cooler_on))
        self.__check_success(error_value, "Check if cooler is on")
        if (cooler_on.value != 1):
            print("Error: Cooler not on", "Exiting...")
            exit()
        
        # Set the readout mode of the camera 
        read_mode = ctypes.c_int(read_mode_top)     
        error_value = self.andor_dll.SetReadMode(read_mode)
        self.__check_success(error_value,"Set Read Mode")
        
        
        # Set the acquisition mode
        acquisition_mode = ctypes.c_int(acquisition_mode_top)       
        error_value = self.andor_dll.SetAcquisitionMode(acquisition_mode)
        self.__check_success(error_value,"Set Acquisition Mode")
        
        
        # Set exposure time
        exposure_time = ctypes.c_float(exposure_time_top)       # time in seconds
        error_value = self.andor_dll.SetExposureTime(exposure_time)
        self.__check_success(error_value, "Set Exposure Time")
        
        
        # Set trigger mode
        trigger_mode = ctypes.c_int(trigger_mode_top)   
        error_value = self.andor_dll.SetTriggerMode(trigger_mode)
        self.__check_success(error_value, "Set Trigger Mode")
        
        # TODO Set up accumulation and kinetic capture & probs not video
        """
        // only needed for accumulation acquisition 
        
        //float accumulation_cycle_time = .1; // seconds
        //errorValue = SetAccumulationCycleTime(accumulation_cycle_time);
        //if (errorValue != DRV_SUCCESS) {
        //std::cout << "Set accumulation cycle time Error\n";
        //std::cout << "Error: " << errorValue << "\n";
        //}
        
        //Only needed for kinetic capture
        
        //errorValue = SetBaselineClamp(1);
        //if (errorValue != DRV_SUCCESS) {
        //std::cout << "Set Baseline Clamp Error\n";
        //std::cout << "Error: " << errorValue << "\n";
        //}
        
        """
        
        
        # Determine the actual times the camera is using for acquisition
        actual_exposure_time = ctypes.c_float()
        actual_accumulate_time = ctypes.c_float()
        actual_kinetic_time = ctypes.c_float()
        error_value = self.andor_dll.GetAcquisitionTimings(ctypes.byref(actual_exposure_time),ctypes.byref(actual_accumulate_time),ctypes.byref(actual_kinetic_time))
        self.__check_success(error_value, "Get Acquisition Timings")
        
        print('Exposure time is ', actual_exposure_time.value)
        
        # Set the horizontal and vertical binning and the area of the image to be captured
        horizontal_binning = ctypes.c_int(horizontal_binning_top)       # Number of pixels to bin horizontally
        vertical_binning = ctypes.c_int(vertical_binning_top)           # Number of pixels to bin vertically
        horizontal_start = ctypes.c_int(horizontal_start_top)           # Start column of image to be taken (inclusive)
        horizontal_end = ctypes.c_int(horizontal_end_top)       # End column of image to be taken (inclusive)
        vertical_start = ctypes.c_int(vertical_start_top)           # Start row of image to be taken (inclusive)
        vertical_end = ctypes.c_int(vertical_end_top)       # End row of image to be taken (inclusive)
        
        # Determine number of horizontal and vertical pixels, and set the region and settings for image capture
        self.number_x_pixels = horizontal_end_top - horizontal_start_top + 1
        self.number_y_pixels = vertical_end_top - vertical_start_top + 1
        error_value = self.andor_dll.SetImage(horizontal_binning, vertical_binning, horizontal_start, horizontal_end, vertical_start, vertical_end);
        self.__check_success(error_value, "Set Image")

    def __initialize_NI_DAQ(self, initialize_array):
        """Initialize the NI daq to be ready to read in voltages
        
        Parameters
        ----------
        initialize_array : initialization array, numpy array
            This contains information from the "NI_DAQ/NI_DAQ properties.ini" file 
        """
        
        self.number_of_reads = int(initialize_array[0])  # determine number voltages to average over
        directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
        LabVIEW = win32com.client.Dispatch("Labview.Application")   # Start running Labview
        self.pci0VI = LabVIEW.getvireference(directory_path + '\\NI_DAQ\\get_average_photodiode_voltage.vi')    # get the path to the LabVIEW VI
    
    def __initialize_IC(self, initialize_array):
        """Initialize the Imaging source camera to be ready to read in voltages
        
        Parameters
        ----------
        initialize_array : initialization array, numpy array
            This contains information from the "NI_DAQ/NI_DAQ properties.ini" file 
        """        
        self.ic_ic = IC_ImagingControl()    # initialize the imaging control grabber
        self.ic_ic.init_library()   # Use the grabber to initialze the library of IC functions we can use

        # Determine the Imaging Source cameras connected to the computer
        cam_names = self.ic_ic.get_unique_device_names()
        if (len(cam_names) ==0):    # no IC camera is connected
            print("Error: No IC cameras connected to the computer.")
            exit()
        print("\nThese are the available cameras:")
        print(cam_names)
        print("Please select an IC camera to use by inputting the index of the camera.")
        print("The indices go from 0 to ", len(cam_names)-1)

        # Iterate through an infinite loop until the user defines which camera they want to use
        while True:
            index = int(input())
            if ((index <= len(cam_names)-1) and (index >= 0)):
                self.cam = self.ic_ic.get_device(cam_names[index])
                break
            else:
                print("You didn't enter a correct index.")

        self.cam.open() # open the camera they chose


        # Go through an infinite loop with user to decide to initialize with the .ini file or by setting all of the values
        print("\nWould you like to set all of the camera initialization values yourself, or use the IC properties.ini file?")
        print('Enter either "set" for setting all of the values or "ini" for the .ini file')
        while True:
            init = input()
            if (init == "set"):
                set_all = True
                break
            elif (init == "ini"):
                set_all = False
                break
            else:
                print("You didn't enter 'set' or 'ini'. Try again.")

        # reset all properties before setting them
        self.cam.reset_properties()
        
        # Go through each property available and set its value
        cam_properties = self.cam.list_property_names()
        print("Note: this only goes through the camera properties available for this specific camera.")
        for attribute_index in range(len(cam_properties)):      # for loop through each of the camera properties
            if (getattr(self.cam,cam_properties[attribute_index]).available == True):   # if the attribute can be set
                if (set_all == True):   # if the user wants to set everything 
                    print("You are setting the", cam_properties[attribute_index])
                    print("Its current value is ", getattr(self.cam,cam_properties[attribute_index]).value)
                    print("The range of values you can set this to is ", getattr(self.cam,cam_properties[attribute_index]).range)
                    print("What would you like to set this property to?")
                    while True:
                        change_value = input()
                        print("You entered", change_value, "\nIs this okay? (enter 'y' or 'n')")
                        input_is_good = input()
                        if (input_is_good == 'y'):
                            break
                        elif(input_is_good == 'n'):
                            print("Type in what you'd like to change this property to instead")
                        else:
                            print("You didn't enter a y or an n. Enter what value you'd like to change the property to again.")
                else:   # if the user is using the .ini file
                    if (initialize_array[attribute_index] == "auto"):   # if the .ini file has "auto" for this property
                        if (getattr(self.cam,cam_properties[attribute_index]).auto_available == True):
                            getattr(self.cam,cam_properties[attribute_index]).auto = True
                            print("Set the camera", cam_properties[attribute_index], "to auto")
                        else:
                            print("Auto setting unavailable for", cam_properties[attribute_index])
                            print("Did not set", cam_properties[attribute_index])
                    elif (initialize_array[attribute_index] == "none"): # if the .ini file has "none" for this property
                        print("Did not set", cam_properties[attribute_index])
                    else:   # if the .ini file has a value for its setting
                        if (type(getattr(self.cam,cam_properties[attribute_index]).value) == int):
                            getattr(self.cam,cam_properties[attribute_index]).value = int(initialize_array[attribute_index])
                        if (type(getattr(self.cam,cam_properties[attribute_index]).value) == float):
                            getattr(self.cam,cam_properties[attribute_index]).value = float(initialize_array[attribute_index])
                        print("Set the camera", cam_properties[attribute_index], "to", getattr(self.cam,cam_properties[attribute_index]).value, "within the range", getattr(self.cam,cam_properties[attribute_index]).range)

        # the last property in the .ini file is whether the person wants the trigger
        self.software_trigger = (initialize_array[len(cam_properties)]) == "True"   # set the software trigger to True or False

        # Determine the video format the user would like to use
        formats = self.cam.list_video_formats()
        print("\nThese are the available video formats:")
        print(formats)
        print("Please select video format to use by inputting the index of the format.")
        print("The indices go from 0 to ", len(formats)-1)

        # Iterate through an infinite loop until the user defines which video format they want to use
        while True:
            self.video_index = int(input())
            if ((self.video_index <= len(formats)-1) and (self.video_index >= 0)):
                self.cam.set_video_format(formats[self.video_index])
                break
            else:
                print("You didn't enter a correct index.")
        current_video_format = self.cam.get_video_format(self.video_index)  # set the video format

        # if the video format stores the pixels left to right and top to bottom, set flip_image to True
        if any(string in str(current_video_format) for string in PIXEL_FORMAT_TOP_DOWN):
            self.flip_image = True
        else:
            self.flip_image = False

        self.cam.enable_continuous_mode(True)        # image in continuous mode
        self.cam.start_live(show_display=False)       # start imaging

        self.cam.enable_trigger(self.software_trigger)                # camera will wait for trigger
        if not self.cam.callback_registered:
            self.cam.register_frame_ready_callback() # needed to wait for frame ready callback

        # determine the image dimensions
        self.width, self.height, depth, color_format = self.cam.get_image_description()
        self.depth = depth // 8 # I have no idea why the open source pyicic library does this

        # take an image because for some cameras, the first image doesn't work correctly and then the rest work
        self.acquire()


    def __initialize_pico(self, initialize_array):
        ps = ps2000a.PS2000a()

        channelRange = ps.setChannel('A', 'DC', 2.0, 0.0, enabled=True,
								        BWLimited=False)
        channelRange = ps.setChannel('B', 'DC', 10.0, 0.0, enabled=True,
								        BWLimited=False)
        # print("Chosen channel range = %d" % channelRange)

        ps.setSimpleTrigger('B', -4.0, 'Falling', delay=0, timeout_ms=100, enabled=True)

        self.ps = ps


    def figure_of_merit(self):
        """Determine the figure of merit using the selected device

        Parameters
        ----------
        fom_num: figure of merit number, int
            This determines which calculation to use when calculating the figure of merit
        """
        self.acquire()
        if (self.device == DAQ_DEVICES[0]): # if the device name is "Andor"
            figure_of_merit_f.Andor_FOM(self.image, self.fom_num)
        elif (self.device == DAQ_DEVICES[1]):   # if the device name is "NI_DAQ"
            figure_of_merit_f.NI_DAQ_FOM(self.voltage, self.fom_num)
        elif (self.device == DAQ_DEVICES[2]):   # if the device name is "IC"
            figure_of_merit_f.ic_FOM(self.frameout, self.fom_num)
        elif (self.device == DAQ_DEVICES[3]):   # if the device name is "Picoscope"
            figure_of_merit_f.pico_FOM(self.data, self.fom_num)

    
    def acquire(self):
        """Acquire data from the appropriate data acquisition hardware
        """
        if (self.device == DAQ_DEVICES[0]): # if the device name is "Andor"
            self.__acquire_andor()
        elif (self.device == DAQ_DEVICES[1]):   # if the device name is "NI_DAQ"
            self.__acquire_NI_DAQ()
        elif (self.device == DAQ_DEVICES[2]):   # if the device name is "IC"
            self.__acquire_IC()
        elif (self.device == DAQ_DEVICES[3]):   # if the device name is "Picoscope"
            self.__acquire_pico()
    
    def __acquire_andor(self):
        """This function acquires an image from the andor camera and returns the image
        """

        # Wait until the camera is in an idle state
        camera_status = ctypes.c_int()
        error_value = self.andor_dll.GetStatus(ctypes.byref(camera_status))
        self.__check_success(error_value, "Get Camera Status")
        while (camera_status.value != DRV_IDLE):    
            error_value = self.andor_dll.GetStatus(ctypes.byref(camera_status))
            self.__check_success(error_value, "Get Camera Status")
    
        # Start the acquisition process 
        error_value = self.andor_dll.StartAcquisition()
        acquiring = self.__check_success(error_value, "Start Acquisition")
        if (acquiring == False):
            self.andor_dll.AbortAcquisition()
        
        
        # Wait until the acquisition is complete
        error_value = self.andor_dll.GetStatus(ctypes.byref(camera_status))
        self.__check_success(error_value, "Get Camera Status")
        while (camera_status.value != DRV_IDLE): 
            error_value = self.andor_dll.GetStatus(ctypes.byref(camera_status))
            self.__check_success(error_value, "Get Camera Status")
        
        # Get the image data from the camera
        size = ctypes.c_int(self.number_x_pixels*self.number_y_pixels)
        image_pointer = ctypes.cast(ctypes.create_string_buffer( size.value*ctypes.sizeof(ctypes.c_long()) ),ctypes.POINTER(ctypes.c_long))
        error_value = self.andor_dll.GetAcquiredData(image_pointer, size)
        self.__check_success(error_value, "Get Acquired Data")
        
        # Deep copy the image from dereferencing a pointer to a numpy array
        image = np.zeros((self.number_y_pixels,self.number_x_pixels))
        for x in range(self.number_x_pixels):
            for y in range(self.number_y_pixels):
                image[y,x] = image_pointer[x + y*self.number_x_pixels]


        self.image = image

    
    def __acquire_NI_DAQ(self):
        """Compute figure of merit that is average voltage reading from DAQ
        """
        
        self.pci0VI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path
        self.pci0VI.setcontrolvalue('error in (no error)', 0)   # set error in
        self.pci0VI.setcontrolvalue('number of reads', self.number_of_reads)   # set addresses
        self.pci0VI.Call()   # Run the VI
        voltage = self.pci0VI.getcontrolvalue('voltage')    # retrieve error out
        error = self.pci0VI.getcontrolvalue('error out')    # retrieve error out
        if (error[1] != 0):   # check whether there was an error
            print('There was an error writing to board 0 at PXI4::5::INSTR')
            print('Error: ', error)
            print('Press anything and enter to exit...')
            input()
            exit()
        self.voltage = voltage
    
    def __acquire_IC(self):
        """Compute figure of merit that is average voltage reading from DAQ
        """
        self.cam.reset_frame_ready()    # reset the frame ready flag to False so that we can wait for the frame to be ready

        if (self.software_trigger):
            self.cam.send_trigger()     # send a software trigger if it was specified to do so

        self.cam.wait_til_frame_ready(1000)              # wait for frame ready due to trigger

        data, width, height, depth = self.cam.get_image_data()  # Get the image from the camera
        frame = np.ndarray(buffer=data,dtype=np.uint8,shape=(self.height, self.width, self.depth))  # turn this buffer into a numpy array
        frameout = copy.deepcopy(frame) # deep copy this data so that if anything overwrites the camera memory, we still have the image

        if self.flip_image:     # if the pixels are written top to bottom, flip the image upside down
            frameout = np.flipud(frameout)

        #plt.imshow(frameout, cmap=plt.get_cmap('gray'))
        #plt.colorbar()
        #plt.show()
        
        del frame   # take care of memory allocation

        self.frameout = frameout    # save the image
        
    def __acquire_pico(self):
        waveform_desired_duration = 1e-4
        obs_duration = 3 * waveform_desired_duration
        sampling_interval = obs_duration / 4096
    
        (actualSamplingInterval, nSamples, maxSamples) = \
    	    self.ps.setSamplingInterval(sampling_interval, obs_duration)
    
        # ps.runBlock()
        # ps.waitReady()
        # # print("Waiting for awg to settle.")
        # time.sleep(0)
        self.ps.runBlock()
        self.ps.waitReady()
        # print("Done waiting for trigger")
        dataA = self.ps.getDataV('A', nSamples, returnOverflow=False)
        # dataB = ps.getDataV('B', nSamples, returnOverflow=False)

    def shut_down(self):
        """Shut down the appropriate data acquisition hardware
        """
        if (self.device == DAQ_DEVICES[0]):    # if the device name is "Andor"
            self.__shut_down_andor()
        elif (self.device == DAQ_DEVICES[1]): # if the device name is "NI_DAQ"
            self.__shut_down_NI_DAQ()
        elif (self.device == DAQ_DEVICES[2]):     # if the device name is "IC"
            self.__shut_down_IC()
        elif (self.device == DAQ_DEVICES[3]):     # if the device name is "Picoscope"
            self.__shut_down_pico()
    
    def __shut_down_andor(self):
        """Shut down the Andor camera
        """
        error_value = self.andor_dll.ShutDown()
        self.__check_success(error_value, "Shut down")
    
    def __shut_down_NI_DAQ(self):
        """Nothing needs to be done to shut down the NI DAQ device
        """
        return
    
    def __shut_down_IC(self):
        """Snut down the camera and the IC grabber
        """
        self.cam.stop_live() # stop capturing video from the camera
        self.cam.close() # shut down the camera

        self.ic_ic.close_library()   # stop accessing the IC dll

    def __shut_down_pico(self):
        self.ps.stop()
        self.ps.close()


if __name__ == "__main__":

    device = data_acqusition("IC", 4)
    for i in range(1):
        device.figure_of_merit()
    device.shut_down()
    # # device = data_acqusition("Andor", 1)
    # device.acquire()
    # device.shut_down()