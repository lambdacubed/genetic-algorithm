#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains classes for all of the available data acquisition devices.


Attributes
----------
DAQ_DEVICES : tuple
    A tuple of strings which correspond to specific data acquisition devices.
DRV_SUCCESS : int
    Andor error code which is given in the sdk pdf file.
DRV_IDLE : int
    Andor error code which is given in the sdk pdf file.
PIXEL_FORMAT_TOP_DOWN : tuple
    Pixel formats as strings for imaging source cameras which organize pixels top down 
    instead of down up.

"""
# TODO comment the lines in this code


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


DAQ_DEVICES = ("Andor", "NI_DAQ", "IC", "Picoscope", "Test")
DRV_SUCCESS = 20002
DRV_IDLE = 20073
PIXEL_FORMAT_TOP_DOWN = ('Y800', 'YGB0', 'YGB1', 'UYBY', 'Y16')


def initialize_daq_device(device_string, fom_num):
    """
    This returns the data acquisition object corresponding to the name in device_string

    ...

    Parameters
    ----------
    device_string : str
        A string naming which daq device to use.
    fom_num : int
        An int denoting which figure of merit this daq device will be using.
    
    Returns
    -------
    daq_device 
        A data acquisition device object
    """
    if (device_string == DAQ_DEVICES[0]):  # if the device name is "Andor"
        return Andor(device_string, fom_num)
    elif (device_string == DAQ_DEVICES[1]):    # if the device name is "NI_DAQ"
        return NI_DAQ(device_string, fom_num)
    elif (device_string == DAQ_DEVICES[2]):    # if the device name is "IC"
        return IC(device_string, fom_num)
    elif (device_string == DAQ_DEVICES[3]):    # if the device name is "Picoscope"
        return Picoscope(device_string, fom_num)
    elif (device_string == DAQ_DEVICES[4]):    # if the device name is "Test"
        return Test(fom_num)
    else:
        print("Error: The device you entered into data acquisition wasn't valid")
        print("The possible devices are: ", DAQ_DEVICES)
        exit()



class daq_device(object):
    """
    This is a data acquisition device used for figure of merit calculation
    
    ...

    Attributes
    ----------
    device : str
        The device which this class corresponds to.
    initialize_array : numpy array
        A numpy array containing information for initializing this device from its .ini file.
    fom_num : int
        The figure of merit number this device will be using.

    """
    def __init__(self, device, fom_num):
        self.device = device    # save which acquisition device is being used
        self.initialize_array = file_f.read_initialization_variables("\\"+ self.device + "\\" + self.device + " properties.ini") # read in the initialization information from the file at device/device properites.ini
        self.fom_num = fom_num  # save the desired figure of merit number
        



class Andor(daq_device):
    """
    This sets up image acquisition for the Andor camera in the LWFA chamber (DL-604M-OEM)

    ...

    Attributes
    ----------
    andor_dll : unsure what type
        The dll for the Andor camera.
    number_x_pixels : int
        The number of pixels in the horizontal direction of the pictures the camera will take
    number_y_pixels : int
        The number of pixels in the vertical direction of the pictures the camera will take
    image : numpy array
        The image the Andor camera just captured
    
    Methods
    -------
    figure_of_merit
        Measure the figure of merit of the system.
    shut_down
        Shut down the Andor camera.

    """

    def __init__(self, device_string, fom_num):	
        """
        Initialize the Andor camera.

        This will turn on the camera, set all of the relevant parameters in the .ini file like 
        exposure time, gain, binning, etc. and depending on the figure of merit number it will 
        also generate a mask and take a background image.

        Parameters
        ----------
        device_string : str
            A string naming which daq device to use.
        fom_num : int
            An int denoting which figure of merit this daq device will be using.

        """
        super().__init__(device_string, fom_num)    # call the daq_device __init__ function
        
        read_mode_top = int(self.initialize_array[0])    # readout mode options: 0 Full Vertical binning;    1 Multi-Track;  2 Random-Track;  3 Single-Track;    4 Image;
        acquisition_mode_top = int(self.initialize_array[1])     # acquisition mode options: 1 Single scan;  2 Accumulate;   3 Kinetics;  4 Fast Kinetics;   5 Run till abort;
        exposure_time_top = float(self.initialize_array[2])      # time in seconds
        trigger_mode_top = int(self.initialize_array[3])     # trigger mode options: 0 internal; 1 external; 6 external start;   7 external exposure (bulb); 9 external FVB EM;  10 software trigger;    12 external charge shifting;
        horizontal_binning_top = int(self.initialize_array[4])   # set the horizontal binning
        vertical_binning_top = int(self.initialize_array[5])     # set the vertical binning
        horizontal_start_top = int(self.initialize_array[6])     # set the horizontal start pixel of the subregion of the camera which to take a picture from
        horizontal_end_top = int(self.initialize_array[7])       # set the horizontal end pixel
        vertical_start_top = int(self.initialize_array[8])   # set the vertical start pixel
        vertical_end_top = int(self.initialize_array[9])     # set the vertical end pixel
        
        
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
        
        # Check Image parameters
        if(horizontal_start_top > horizontal_end_top or vertical_start_top > vertical_end_top):
            print("Image start positions must not be greater than end positions")

        if(horizontal_start_top < 1 or horizontal_end_top > gblXPixels.value):
            print("Image horizontal positions must be >0 and <detector width");

        if(vertical_start_top < 1 or vertical_end_top > gblYPixels.value):
        	print("Image vertical positions must be >0 and <detector height");
        
        if((horizontal_end_top - horizontal_start_top + 1) % horizontal_binning_top!=0):
            print("Image width must be a multiple of Horizontal Binning");
            print("Total number of horizontal pixels: ", gblXPixels.value)
            print("Current image width: ", horizontal_end_top - horizontal_start_top + 1, "pixels")
            print("Current horizontal binning is: ", horizontal_binning_top)

        if((vertical_end_top - vertical_start_top + 1) % vertical_binning_top!=0):
            print("Image height must be a multiple of Vertical Binning");
            print("Total number of vertical pixels: ", gblYPixels.value)
            print("Current image height: ", vertical_end_top - vertical_start_top + 1)
            print("Current vertical binning is :", vertical_binning_top)


        # Determine number of horizontal and vertical pixels, and set the region and settings for image capture
        self.number_x_pixels = int((horizontal_end_top - horizontal_start_top + 1) / horizontal_binning_top)
        self.number_y_pixels = int((vertical_end_top - vertical_start_top + 1) / vertical_binning_top)
        error_value = self.andor_dll.SetImage(horizontal_binning, vertical_binning, horizontal_start, horizontal_end, vertical_start, vertical_end);
        self.__check_success(error_value, "Set Image")

        while True:
            print("\nInput 'capture' to capture and display the Andor camera image and 'ready' when ready to save it as background image")
            command = input()
            if command == "ready":
                break
            elif command == 'capture':
                print("Close the image window to continue the program")
                self.__acquire()
                figure_of_merit_f.Andor_FOM(self.image, "test")
            else:
                print("You didn't enter a correct input")
        self.__acquire()
        self.background_image = self.image

        if fom_num == 2:
            while True:
                print("\nInput 'capture' to capture and display the Andor camera image and 'ready' when ready to take an image (minus the background) to determine the image centroid for the Gaussian mask")
                command = input()
                if command == "ready":
                    break
                elif command == 'capture':
                    print("Close the image window to continue the program")
                    self.__acquire()
                    figure_of_merit_f.Andor_FOM(self.image-self.background_image, "test")
                else:
                    print("You didn't enter a correct input")

            self.__acquire()
            image = self.image - self.background_image
            moment00 = np.sum(image)
            sum = 0
            for x in range(self.number_x_pixels):
                sum += (x+1) * np.sum(image[:,x])
            moment10 = sum

            sum = 0
            for y in range(self.number_y_pixels):
                sum += (y+1) * np.sum(image[y,:])
            moment01 = sum

            mu_x = (moment10-1)/moment00
            mu_y = (moment01-1)/moment00

            mu_x = 28
            mu_y = 32
            print("Image centroid at (", mu_x, ", ", mu_y, ")")

            #sigma of 5 used for focusing beam
            #signam 9 used for repositioning
            sigma_x = 5
            sigma_y = 5

            gaussian_weight = np.zeros_like(image)
            for x in range(gaussian_weight.shape[1]):
                for y in range(gaussian_weight.shape[0]):
                    gaussian_weight[y,x] = np.exp(-np.power(x - mu_x, 2.) / (2 * np.power(sigma_x, 2.)) - np.power(y - mu_y, 2.) / (2 * np.power(sigma_y, 2.)))


            self.gaussian_weight = gaussian_weight
            print("This is the gaussian weighting function:")
            figure_of_merit_f.Andor_FOM(self.gaussian_weight, "test")


        if fom_num == 1 or fom_num == 2:
            while True:
                print("\nInput 'capture' to capture and display the Andor camera image minus the background and 'ready' when ready to determine the mask in which to sum the pixels")
                command = input()
                if command == "ready":
                    break
                elif command == 'capture':
                    print("Close the image window to continue the program")
                    self.__acquire()
                    figure_of_merit_f.Andor_FOM(self.image-self.background_image, "test")
                else:
                    print("You didn't enter a correct input")

            print("Input the central x pixel of the ellipse (in pixels)")
            x_center = int(input())
            print("Input the central y pixel of the ellipse (in pixels)")
            y_center = int(input())

            print("Input the horizontal radius of the ellipse (in pixels)")
            x_radius = int(input())
            print("Input the vertical radius of the ellipse (in pixels)")
            y_radius = int(input())

            mask = np.zeros_like(self.image)
            for x in range(mask.shape[0]):
                for y in range(mask.shape[1]):
                    mask[y,x] = (((x-x_center)/x_radius)**2 + ((y-y_center)/y_radius)**2) < 1
            self.mask = mask
            
            print("This is the mask:")
            figure_of_merit_f.Andor_FOM(self.mask, "test")

            print("This is the image minus background multiplied by the mask")
            figure_of_merit_f.Andor_FOM(self.mask * (self.image - self.background_image), "test")

        if fom_num == 2:
            print("This is the gaussian weighting function multiplied by the mask:")
            figure_of_merit_f.Andor_FOM(self.mask * self.gaussian_weight, "test")
            self.gaussian_mask = self.mask * self.gaussian_weight

    def __check_success(self, error_value, function_name):
        """
        Determine if calling the Andor function worked
        
        There are various functions which set exposure time or check if the cooler is on. This function
        makes sure the return value from all of those functions was DRV_SUCCESS.S
        
        Parameters
        ----------
        error_value : int
            This is the error value returned from any Andor function
        function_name : str
            This is a string which denotes which function returned this error value
        """
        if (error_value != DRV_SUCCESS):    # if the error value wasn't success
            print("Andor", function_name,"Error", error_value)
            exit()

    def figure_of_merit(self):
        """
        Measure the figure of merit.

        Acquire an image using the Andor camera and measure its figure of merit.

        Returns
        -------
        int, float
            The figure of merit of the image which was taken

        """
        self.__acquire()
        self.image = self.image - self.background_image
        if self.fom_num == "test":
            return figure_of_merit_f.Andor_FOM(self.image, self.fom_num)
        elif self.fom_num == 1:
            self.image = self.image * self.mask
            return figure_of_merit_f.Andor_FOM(self.image, self.fom_num)
        elif self.fom_num == 2:
            self.image = self.image * self.gaussian_mask
            return figure_of_merit_f.Andor_FOM(self.image, self.fom_num)

    def __acquire(self):
        """
        Acquire an image from the Andor camera.

        The Andor camera acquires an image and then saves the image as self.image

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


        self.image = image  # save the image

    def shut_down(self):
        """
        Shut down the Andor camera.

        ...

        """
        error_value = self.andor_dll.ShutDown()
        self.__check_success(error_value, "Shut down")


class NI_DAQ(daq_device):
    """
    NI data acquisition device

    National Instruments data acquisition device connected to the computer via a PCI cable

    Attributes
    ----------
    number_of_reads : int
        Number of voltage readings to take from the device
    pci0VI : LabVIEW reference
        A LabVIEW VI reference in python to the VI which reads voltages
    voltage : float
        The voltage read from the device

    Methods
    -------
    figure_of_merit
        Measure the figure of merit of the system.
    shut_down
        Shut down the NI DAQ device.

    """

    def __init__(self, device_string, fom_num):
        """
        Initialize the national instruments daq device.

        Set the number of reads to take from the NI DAQ device and initialize the LabVIEW VI reference.

        Parameters
        ----------
        device_string : str
            A string naming which daq device to use.
        fom_num : int
            An int denoting which figure of merit this daq device will be using.

        """
        super().__init__(device_string, fom_num)    # call the daq_device __init__ function
        
        self.number_of_reads = int(self.initialize_array[0])  # determine number voltages to average over
        directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
        LabVIEW = win32com.client.Dispatch("Labview.Application")   # Start running Labview
        self.pci0VI = LabVIEW.getvireference(directory_path + '\\NI_DAQ\\get_average_photodiode_voltage.vi')    # get the path to the LabVIEW VI

    def figure_of_merit(self):
        """
        Determine the figure of merit by using the voltages from the NI DAQ device

        Measure the voltages from the device and then determine the figure of merit

        Returns
        -------
        int, float
            Figure of merit of the data collected

        """
        self.__acquire()    # acquire voltages
        return figure_of_merit_f.NI_DAQ_FOM(self.voltage, self.fom_num)

    
    def __acquire(self):
        """
        Read the voltages from the NI DAQ device.

        Call the LabVIEW VI which reads voltages from the device and then save the 
        output of that VI as the attribute voltage. 

        """
        self.pci0VI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path
        self.pci0VI.setcontrolvalue('error in (no error)', 0)   # set error in
        self.pci0VI.setcontrolvalue('number of reads', self.number_of_reads)   # set addresses
        self.pci0VI.Call()   # Run the VI
        voltage = self.pci0VI.getcontrolvalue('voltage')    # retrieve error out
        error = self.pci0VI.getcontrolvalue('error out')    # retrieve error out
        if (error[1] != 0):   # check whether there was an error
            print('There was an error getting data from NI_DAQ')
            print('Error: ', error)
            print('Press anything and enter to exit...')
            input()
            exit()
        self.voltage = voltage  # save the voltage

    def shut_down(self):
        """
        Nothing needs to be done to shut down the NI DAQ device.

        """
        return

class IC(daq_device):
    """
    This class sets up data acquisition for (theoretically) all cameras from the imaging source.

    This sets all of the camera properties relevant to a given camera. It utilizes the py-ic-ic wrapper 
    downloaded from github for the IC C library given on the imaging source website. It seems to mostly
    work, but it takes a few tries to figure out how to use this program with each model of camera. 
    Test out different parameters in the .ini file until you get a good image from the camera.

    Attributes
    ----------
    ic_ic : idk what type
        IC library grabber.
    cam : idk what type
        Camera being used.
    software_trigger : bool
        A boolean value which determines whether to use a software trigger or not.
    video_index : int
        An index which determines which video format the camera will be using.
    width : int
        The horizontal number of pixels used in the image being captured.
    height : int
        The vertical number of pixels used in the image being captured.
    depth : int
        The number of color channels used in the image being captured.

    Methods
    -------
    figure_of_merit
        Measure the figure of merit of the system.
    shut_down
        Shut down the Imaging Source camera.

    """

    def __init__(self, device_string, fom_num):
        """
        Initialize the Imaging Source camera.

        Set all of the parameters for the chosen Imaging Source camera so that it is ready to 
        take an image.

        Parameters
        ----------
        device_string : str
            A string naming which daq device to use.
        fom_num : int
            An int denoting which figure of merit this daq device will be using.

        """
        super().__init__(device_string, fom_num)     # call the daq_device __init__ function

        
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
                    if (self.initialize_array[attribute_index] == "auto"):   # if the .ini file has "auto" for this property
                        if (getattr(self.cam,cam_properties[attribute_index]).auto_available == True):
                            getattr(self.cam,cam_properties[attribute_index]).auto = True
                            print("Set the camera", cam_properties[attribute_index], "to auto")
                        else:
                            print("Auto setting unavailable for", cam_properties[attribute_index])
                            print("Did not set", cam_properties[attribute_index])
                    elif (self.initialize_array[attribute_index] == "none"): # if the .ini file has "none" for this property
                        print("Did not set", cam_properties[attribute_index])
                    else:   # if the .ini file has a value for its setting
                        if (type(getattr(self.cam,cam_properties[attribute_index]).value) == int):
                            getattr(self.cam,cam_properties[attribute_index]).value = int(self.initialize_array[attribute_index])
                        if (type(getattr(self.cam,cam_properties[attribute_index]).value) == float):
                            getattr(self.cam,cam_properties[attribute_index]).value = float(self.initialize_array[attribute_index])
                        print("Set the camera", cam_properties[attribute_index], "to", getattr(self.cam,cam_properties[attribute_index]).value, "within the range", getattr(self.cam,cam_properties[attribute_index]).range)

        # the last property in the .ini file is whether the person wants the trigger
        self.software_trigger = (self.initialize_array[len(cam_properties)]) == "True"   # set the software trigger to True or False

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
        self.__acquire()

    def figure_of_merit(self):
        """
        Determine the figure of merit using the Imaging Source camera.

        Capture an image using the imaging source camera and then calculate the figure of merit.
        
        """
        self.__acquire()    # acquire an image from the camera
        return figure_of_merit_f.ic_FOM(self.frameout, self.fom_num)

    
    def __acquire(self):
        """
        Capture an image.

        Capture an image using the given IC camera and then save the image as frameout.

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
        
        del frame   # take care of memory allocation

        self.frameout = frameout    # save the image
        

    def shut_down(self):
        """
        Shut down the camera and close the IC grabber.

        """
        self.cam.stop_live() # stop capturing video from the camera
        self.cam.close() # shut down the camera

        self.ic_ic.close_library()   # stop accessing the IC dll



class Picoscope(daq_device):
    """
    The picoscope as a data acquisition device.

    ...

    Attributes
    ----------
    channels : tuple of str
        The available channels to use in the program, channel A and channel B.
    signal_channel : str
        The channel which te signal will be read from.
    nSamples : int
        The number of samples to take when acquiring data.
    ps : object from ps2000a library
        The reference to the picoscope device.
    data : list or numpy array
        The data acquired when reading the picoscope device.

    Methods
    -------
    figure_of_merit
        Measure the figure of merit of the system.
    shut_down
        Shut down the Imaging Source camera.

    """

    def __init__(self, device_string, fom_num):
        """
        Set up the picoscope for data acquisition.

        Determine the channel to read from, how to trigger the device, how many samples to read, etc.
        to acquire data properly.

        Parameters
        ----------
        device_string : str
            A string naming which daq device to use.
        fom_num : int
            An int denoting which figure of merit this daq device will be using.

        """
        super().__init__(device_string, fom_num)    # call the daq_device __init__ function

        self.channels = ('A', 'B')  # the only possible channels are 'A' and 'B'

        ps = ps2000a.PS2000a()  # create an instance of the picoscope 2000a class

        channelA_coupling = self.initialize_array[0]    # DC or AC coupling
        channelA_voltage_range = float(self.initialize_array[1])    # The voltage range is [-voltage_range, +voltage_range] (excluding offset)
        channelA_offset = float(self.initialize_array[2])   # This is an offset that the scope will add to your signal.
        channelA_enabled = self.initialize_array[3] == "True"   # determine if the channel is enabled
        channelA_bandwidth_limited = self.initialize_array[4] == "True" # determine if the channel should use bandwidth limiting

        channelB_coupling = self.initialize_array[5]    # DC or AC coupling
        channelB_voltage_range = float(self.initialize_array[6])    # The voltage range is [-voltage_range, +voltage_range] (excluding offset)
        channelB_offset = float(self.initialize_array[7])   # This is an offset that the scope will add to your signal.
        channelB_enabled = self.initialize_array[8] == "True"   # determine if the channel is enabled
        channelB_bandwidth_limited = self.initialize_array[9] == "True" # determine if the channel should use bandwidth limiting

        # Initialize channel A with all of the desired parameters  
        channelARange = ps.setChannel(self.channels[0], channelA_coupling, channelA_voltage_range, channelA_offset, channelA_enabled, channelA_bandwidth_limited, probeAttenuation=1.0)
        print("Channel A range is ", channelARange)

        # Initialize channel B with all of the desired parameters  
        channelBRange = ps.setChannel(self.channels[1], channelB_coupling, channelB_voltage_range, channelB_offset, channelB_enabled, channelB_bandwidth_limited, probeAttenuation=1.0)
        print("Channel B range is ", channelBRange)
        
        trigger_channel = self.initialize_array[10] # the trigger channel
        trigger_threshold = float(self.initialize_array[11])    # threshold in volts to activate trigger
        trigger_direction = self.initialize_array[12]   # "Rising" or "Falling" trigger
        trigger_delay = int(self.initialize_array[13])  # number of clock cycles to wait from trigger conditions met until we actually trigger capture
        trigger_timeout = int(self.initialize_array[14])    # time to wait in mS for the trigger to occur. If no trigger occurs it gives up & auto-triggers.
        trigger_enabled = self.initialize_array[15] == "True"   # determine whether triggering is enabled
        
        # Set up the trigger according to the input parameters
        ps.setSimpleTrigger(trigger_channel, trigger_threshold, trigger_direction, trigger_delay, trigger_timeout, trigger_enabled)

        self.signal_channel = self.initialize_array[16] # the channel which will be the signal
        acquisition_window_duration = float(self.initialize_array[17])  # the duration of the signal acquisition window

        # idk what or why they do this, Jinpu said to do this because it was done this way in the pico-python example 
        obs_duration = 3 * acquisition_window_duration
        sampling_interval = obs_duration / 4096

        # set up the sampling interval
        (actualSamplingInterval, self.nSamples, maxSamples) = ps.setSamplingInterval(sampling_interval, obs_duration)
        print("Sampling interval:", actualSamplingInterval, "\nNumber of samples:", nSamples)

        self.ps = ps    # save the picoscope object

    def figure_of_merit(self):
        """
        Determine the figure of merit.

        Measure data using the picoscope device and then calculate the figure of merit

        Returns
        -------
        int, float
            Figure of merit of the data collected

        """
        self.__acquire()    # acquire a signal from the picoscope
        return figure_of_merit_f.pico_FOM(self.data, self.fom_num)

    
    def __acquire(self):
        """
        Acquire picoscope data.

        Run the picoscope data acquisition process, wait until it is ready to be read, get the data,
        and save this data as self.data.

        """
        self.ps.runBlock()  # run the picoscope data acquisition 
        self.ps.waitReady() # wait until the scope is ready
        self.data = self.ps.getDataV(self.signal_channel, self.nSamples, returnOverflow=False)  # get the data from the picoscope

    def shut_down(self):
        """
        Shut down the picoscope.

        """
        self.ps.stop()  # stop the picoscope running
        self.ps.close() # close the picoscope connection


class Test(object):
    """
     A data acquisition device which is used for testing

    This device doesn't actually talk to anything. It is used when testing parts of the program 
    unrelated to the data acquisition process. This allows the program to run faster and not run
    into any issues that might occur within the data acquisition process.

    Attributes
    ----------
    fom_num : int
        An int denoting which figure of merit this daq device will be using.

    Methods
    -------
    figure_of_merit
        Measure the figure of merit of the system.
    shut_down
        Shut down the Imaging Source camera.

    """

    def __init__(self, fom_num):
        """
        Save the fom_num.


        Parameters
        ----------
        fom_num : int
            Number denoting which figure of merit to use.

        """
        self.fom_num = fom_num

    def figure_of_merit(self):
        """
        Return a random number.

        Returns
        -------
        float
            The figure of merit is a random number with a Gaussian distribution(mean = 0, std dev = 1)

        """
        return np.random.randn()

    def shut_down(self):
        """
        There is nothing to shut down because this is not a real daq device.

        """
        return
         

if __name__ == "__main__":
    num_tests = 1   # the number of times to acquire data from the device
    fom_num = 2
    # determine which device to test
    print("Which device would you like to test?\nThe options are the following: \n", DAQ_DEVICES)
    print("Enter an index from 0 to ", len(DAQ_DEVICES)-1)
    while True:
        index = int(input())
        if 0 <= index <= len(DAQ_DEVICES)-1:
            break
        else:
            print("You didn't enter a correct index. Try again.")
    
    
    device = initialize_daq_device(DAQ_DEVICES[index], fom_num)    # initialize the device
    for i in range(num_tests):  # for num_test times
        device.figure_of_merit()    # acquire data from the device
    device.shut_down()  # shut the device down
