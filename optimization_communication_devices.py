#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains classes of devices which communicate with optimization 
devices.

Attributes
----------
DEVICES : tuple
    Strings which correspond to classes that communicate with an optimization 
    device

"""


#import pyvisa   # Use this when using the pyvisa code in send_to_board pci
import win32com.client  # Use this when using the LabVIEW VI in send_to_board # Python ActiveX Client
import numpy as np  # general useful python library
import os
import ctypes   # used when using python as a wrapper for c functions

DEVICES = ("PCI", "USB", "Test")

def initialize_comm_device(device_string):
    """
    Initialize the optimization communication device. 

    Determine which opt comm device the user wishes to use and return that object.

    Parameters
    ----------
    device_string : str
        A string denoting which device to initialize
    
    Returns
    -------
    object
        Optimization communication object.

    """
    if device_string == DEVICES[0]:     # if the device string is "PCI"
        return PCI_DM_comm()
    elif device_string == DEVICES[1]:   # if the device string is "USB"
        return USB_DM_comm()
    elif device_string == DEVICES[2]:   # if the device string is "Test"
        return Test_comm()
    else:
        print("Error: The given mirror communication device was incorrect.")
        exit()

class PCI_DM_comm(object):
    """
    PCI communication with the deformable mirror.

    The PXI cards within the computer which are connected to a high voltage amplifier which then
    sends voltages to the deformable mirror.

    Attributes
    ----------
    ACTUATOR_ADDRESSES : list
        The addresses the LabVIEW program uses to input voltage values into the PXI cards.
    voltage_multiplier : float
        The amount to multiply voltages in the program by so that the output corresponds to 
        the values used within the program.
    waiting_time : float
        Time in seconds to wait after sending voltages to the mirror so that the voltages have 
        time to be processed by the computer and then travek through the amplifier.
    pci5vi : LabVIEW reference
        A LabVIEW VI reference in python to the VI which inputs voltages to the PXI card number 5.
    pci4VI : LabVIEW reference
        A LabVIEW VI reference in python to the VI which inputs voltages to the PXI card number 4.

    Methods
    -------
    write_to_object(genes, mirror)
        write the voltages corresponding to the genes to the given mirror

    """
    def __init__(self):
        """
        Initialize the PCI communication.

        Set all of the relevant parameters for the PCI device and call the LabVIEW VI to set its 
        actuator addresses.

        """
        self.ACTUATOR_ADDRESSES = [[0x34, 0x54, 0x28, 0x38, 0x08, 0x04, 0x24, 0x50, 0x58, 0x2C, 
                                    0x30, 0x1C, 0x10, 0x14, 0x0C, 0x00, 0x3C, 0x20, 0x5C],
                                   [0x24, 0x5C, 0x58, 0x54, 0x20, 0x10, 0x08, 0x1C, 0x14, 
                                    0x0C, 0x04, 0x00, 0x3C, 0x38, 0x34, 0x30, 0x2C, 0x28]]

        self.voltage_multiplier = 2.625   # this is the constant used to multiply the genes to get the correct voltage output
        self.waiting_time = 0.1 # seconds

        directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path

        LabVIEW = win32com.client.Dispatch("Labview.Application")   # Start running Labview
        self.pci5VI = LabVIEW.getvireference(directory_path + '\\LabView send volt to board\\Volt_to_board_0.vi')    # path to the LabVIEW VI for the first board
        self.pci5VI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path
        self.pci5VI.setcontrolvalue('error in (no error)', 0)   # set error in
        self.pci5VI.setcontrolvalue('addresses', self.ACTUATOR_ADDRESSES[0])   # set addresses

        self.pci4VI = LabVIEW.getvireference(directory_path + '\\LabView send volt to board\\Volt_to_board_1.vi')    # path to the LabVIEW VI for the second board
        self.pci4VI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path
        self.pci4VI.setcontrolvalue('error in (no error)', 0)   # set error in
        self.pci4VI.setcontrolvalue('addresses', self.ACTUATOR_ADDRESSES[1])   # set addresses


    def write_to_object(self, genes, mirror):
        """
        Write voltages to the mirror.

        Checks whether the voltage values satisfy the requirements then sends them to the 
        deformable mirror.

        Parameters
        ----------
        genes: 1D numpy array
            the genes to be sent to the mirror
        mirror : object from optimization_devices.py
            The deformable mirror to which the genes are being written.

        """
        if  mirror.fits_object(genes): # if the genes don't break the mirror
            if mirror.zernike_polynomial_mode == True:  # if the mirror is in zernike polynomial mode
                voltages = mirror.zernike_to_voltages(genes)
            else:
                voltages = genes
            applied_voltages = voltages * self.voltage_multiplier # multiply each gene by some mirror constant to get the voltages sent to the mirror
            voltage_array = mirror.array_conversion_PCI(applied_voltages) # change the mapping of the indices
            self.__send_to_board(voltage_array[:19], voltage_array[19:])
        else:
            print("Error: Tried writing the genes to the mirror, but they would've broken it")

    def __send_to_board(self, voltages0, voltages1):
        """
        Write the voltages to the PXI cards

        Parameters
        ----------
        voltages0 : 1D numpy array
            The array of voltages being sent to board 5
        voltages1 : 1D numpy array
            The array of voltages being sent to board 4

        """
        #There are 2 different sets of code to write to the board: calling the LabVIEW VIs themselves and using pyVISA 
        # This is the code for running the LabView VI which communicates with the deformable mirror 
        self.pci5VI.setcontrolvalue('values to write', voltages0.tolist())   # set values to write
        self.pci5VI.Call()   # Run the VI
        result = self.pci5VI.getcontrolvalue('error out')    # retrieve error out
        if (result[1] != 0):   # check whether there was an error
            print('There was an error writing to board 0 at PXI4::5::INSTR')
            print('Error: ', result)
            print('Press anything and enter to exit...')
            input()
            exit()

        self.pci4VI.setcontrolvalue('values to write', voltages1.tolist())   # set values to write
        self.pci4VI.Call()   # Run the VI
        result = self.pci4VI.getcontrolvalue('error out')    # retrieve error out
        if (result[1] != 0):   # check whether there was an error
            print('There was an error writing to board 1 at PXI4::4::INSTR')
            print('Error: ', result)
            print('Press anything and enter to exit...')
            input()
            exit()
    
    
        # This is the code for using pyVISA, but it doesn't support PXI devices at the moment (5/18/2017)
        """
        rm = pyvisa.ResourceManager()   # instantiate an object to manage all devices connected to the computer
        #print(rm.list_resources())  # show which things are connected to the computer
        deformable_mirror = rm.open_resource(PCI_BOARDS[board_num])
        lib = rm.visalib    # access the library for low-level "hardware" functions
        session = lib.open_default_resource_manager() # open hardware level manager of devices attached to the computer
        dm_session = lib.open(session[0], PCI_BOARDS[board_num]) # open access to the correct pci card
        lib.map_address(dm_session[0], pyvisa.constants.VI_PXI_BAR0_SPACE, 0, 0xFF) # connect the pci memory addresses to the program's memory addresses
        print(type(voltages[0]), 'voltages size')
        for i in range(voltages.size):   # for each of the 37 voltages
            lib.poke_8(dm_session[0], ACTUATOR_ADDRESSES[board_num][i], int(voltages[i]))   # write the voltage into the memory accessed by the pci card
        lib.close(session[0])  # close the pci card
        return
        """


class USB_DM_comm(object):
    """
    USB communication with the deformable mirror.

    The USB DAC connects to a high voltage amplifier which sends voltages to a deformable mirror.

    Attributes
    ----------
    voltage_multiplier : float
        The amount to multiply voltages in the program by so that the output corresponds to 
        the values used within the program.
    waiting_time : float
        Time in seconds to wait after sending voltages to the mirror so that the voltages have 
        time to be processed by the computer and then travek through the amplifier.
    usbVI : LabVIEW reference
        A LabVIEW VI reference in python to the VI which inputs voltages to the PXI card number 5.

    Methods
    -------
    write_to_object(genes, mirror)
        write the voltages corresponding to the genes to the given mirror

    """

    def __init__(self):
        """
        Initialize the USB communication.

        ...

        """
        self.voltage_multiplier = 13.72
        self.waiting_time = 0.1 # seconds

        directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path

        LabVIEW = win32com.client.Dispatch("Labview.Application")   # Start running Labview
        self.usbVI = LabVIEW.getvireference(directory_path + '\\Volt_to_mirror_2.vi')    # path to the LabVIEW VI for the first board
        self.usbVI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path

    def write_to_object(self, genes, mirror):
        """
        Write voltages to the mirror.

        Checks whether the voltage values satisfy the requirements then sends them to the 
        deformable mirror.

        Parameters
        ----------
        genes: 1D numpy array
            the genes to be sent to the mirror
        mirror : object from optimization_devices.py
            The deformable mirror to which the genes are being written.

        """
        if mirror.fits_object(genes): # if the genes don't break the mirror
            if mirror.zernike_polynomial_mode == True:
                voltages = mirror.zernike_to_voltages(genes)
            else:
                voltages = genes
            applied_voltages = voltages * self.voltage_multiplier # multiply each gene by some mirror constant to get the voltages sent to the mirror
            voltage_array = mirror.array_conversion_USB(applied_voltages) # change the mapping of the indices
            self.__send_to_board(voltage_array)
        else:
            print("Error: Tried writing the genes to the mirror, but they would've broken it")

    def __send_to_board(self, voltages):
        """
        Send the voltages to the USB DAC.

        Call the LabVIEW VI to send voltages through USB communication.

        Parameters
        ----------
        voltages : 1D numpy array
            The array of voltages being sent to the USB DAC

        """
        self.usbVI.setcontrolvalue('Actuator 1 to 37', voltages.tolist())   # set values to write
        self.usbVI.Call()   # Run the VI
        result = self.usbVI.getcontrolvalue('ERROR STATUS')    # retrieve error out
        # TODO test error out to see if successful
       
class Test_comm(object):
    """
    A testing version of the optimization communication device.

    This is a optimization communication device which does not communicate with anything. This object
    can be called to test out other parts of the algorithm without actually sending any genes to 
    the corresponding optimization object.

    Attributes
    ----------
    waiting_time : float
        Time in seconds to wait after sending voltages to the mirror so that the voltages have 
        time to be processed by the computer and then travek through the amplifier.

    Methods
    -------
    write_to_object(genes, mirror)
        write the voltages corresponding to the genes to the given mirror

    """

    def __init__(self):
        """
        Initialize the test opt comm device.

        """
        self.waiting_time = 0.1 # seconds
        return

    def write_to_object(self, genes, mirror):
        """
        Don't write to anything.

        """
        pass

if __name__ == "__main__":
    print('You meant to run GeneticAlgorithm.py')

