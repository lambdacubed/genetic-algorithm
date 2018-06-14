
#import pyvisa   # Use this when using the pyvisa code in send_to_board pci
import win32com.client  # Use this when using the LabVIEW VI in send_to_board # Python ActiveX Client
import numpy as np  # general useful python library
import os

import ctypes   # used when using python as a wrapper for c functions

DEVICES = ("PCI", "USB", "Test")

def initialize_comm_device(device_string):
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
    def __init__(self):
        self.ACTUATOR_ADDRESSES = [[0x34, 0x54, 0x28, 0x38, 0x08, 0x04, 0x24, 0x50, 0x58, 0x2C, 0x30, 0x1C, 0x10, 0x14, 0x0C, 0x00, 0x3C, 0x20, 0x5C],
                                   [0x24, 0x5C, 0x58, 0x54, 0x20, 0x10, 0x08, 0x1C, 0x14, 0x0C, 0x04, 0x00, 0x3C, 0x38, 0x34, 0x30, 0x2C, 0x28]]

        self.voltage_multiplier = 2.65   # this is the constant used to multiply the genes to get the correct voltage output

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


    def write_to_mirror(self, genes, mirror):
        """Checks whether the voltage values satisfy the requirements then sends them to the deformable mirror

        Parameters
        ----------
        genes: genes, 1D numpy array
            the genes or actuator voltages to be tested
        mirror : object from mirror_functions.py
            This contains the list of neighbors to make sure the genes don't break the mirror.
        """
        if  mirror.fits_mirror(genes): # if the genes don't break the mirror
            applied_voltages = genes * self.voltage_multiplier # multiply each gene by some mirror constant to get the voltages sent to the mirror
            voltage_array = mirror.__array_conversion_PCI(applied_voltages) # change the mapping of the indices
            self.__send_to_board(voltage_array[:19], voltage_array[19:])
        else:
            print("Error: Tried writing the genes to the mirror, but they would've broken it")
        return

    def __send_to_board(self, voltages0, voltages1):
        """Write the voltage values to the PCI boards

        Parameters
        ----------
        voltages0 : voltages, 1D numpy array
            The array of voltages being sent to board 0
        voltages1 : voltages, 1D numpy array
            The array of voltages being sent to board 1

        """
        #There are 3 different sets of code to write to the board: calling the LabVIEW VIs themselves, calling functions in a LabVIEW dll, and using pyVISA 
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
    def __init__(self):
        self.voltage_multiplier = 13.72

        directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path

        LabVIEW = win32com.client.Dispatch("Labview.Application")   # Start running Labview
        self.usbVI = LabVIEW.getvireference(directory_path + '\\Volt_to_mirror_2.vi')    # path to the LabVIEW VI for the first board
        self.usbVI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path

    def write_to_mirror(self, genes, mirror):
        """Checks whether the voltage values satisfy the requirements then sends them to the deformable mirror
        Parameters
        ----------
        genes: genes, 1D numpy array
            the genes or actuator voltages to be tested
        mirror : object from mirror_functions.py
            This contains the list of neighbors to make sure the genes don't break the mirror.
        """
        if mirror.fits_mirror(genes): # if the genes don't break the mirror
            applied_voltages = genes * self.voltage_multiplier # multiply each gene by some mirror constant to get the voltages sent to the mirror
            voltage_array = mirror.__array_conversion_USB(applied_voltages) # change the mapping of the indices
            self.__send_to_board(voltages)
        else:
            print("Error: Tried writing the genes to the mirror, but they would've broken it")

    def __send_to_board(self, voltages):
        """Write the voltage values to the PCI boards
        Parameters
        ----------
        voltages : voltages, 1D numpy array
    	    The array of voltages being sent to the USB DAC
        """
        #There are 3 different sets of code to write to the board: calling the LabVIEW VIs themselves, calling functions in a LabVIEW dll, and using pyVISA 
        # This is the code for running the LabView VI which communicates with the deformable mirror 
    
        self.usbVI.setcontrolvalue('Actuator 1 to 37', voltages.tolist())   # set values to write
        self.usbVI.Call()   # Run the VI
        result = self.usbVI.getcontrolvalue('ERROR STATUS')    # retrieve error out

       
class Test_comm(object):
    def __init__(self):
        return

    def write_to_mirror(self, genes, mirror):
        return

if __name__ == "__main__":
    print('You meant to run GeneticAlgorithm.py')

