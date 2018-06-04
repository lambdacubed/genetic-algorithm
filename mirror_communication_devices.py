
# TODO get rid of labView

#import pyvisa   # Use this when using the pyvisa code in send_to_board pci
import win32com.client  # Use this when using the LabVIEW VI in send_to_board # Python ActiveX Client
import numpy as np  # general useful python library

import ctypes   # used when using python as a wrapper for c functions

DEVICES = ["PCI", "USB"]

def initialize_device(device_string):
    if device_string == DEVICES[0]:     # if the device string is "PCI"
        return PCI_DM_comm()
    elif device_string == DEVICES[1]:   # if the device string is "USB"
        return USB_DM_comm()
    else:
        print("Error: The given mirror communication device was incorrect.")
        exit()

class PCI_DM_comm(object):
    def __init__(self):
        self.ACTUATOR_ADDRESSES = [[0x34, 0x54, 0x28, 0x38, 0x08, 0x04, 0x24, 0x50, 0x58, 0x2C, 0x30, 0x1C, 0x10, 0x14, 0x0C, 0x00, 0x3C, 0x20, 0x5C],
                                   [0x24, 0x5C, 0x58, 0x54, 0x20, 0x10, 0x08, 0x1C, 0x14, 0x0C, 0x04, 0x00, 0x3C, 0x38, 0x34, 0x30, 0x2C, 0x28]]

        self.VOLTAGE_MULTIPLIER = 2.65   # this is the constant used to multiply the genes to get the correct voltage output

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


    def write_to_mirror(genes, mirror):
        """Checks whether the voltage values satisfy the requirements then sends them to the deformable mirror

        Parameters
        ----------
        genes: genes, 1D numpy array
            the genes or actuator voltages to be tested
        mirror : object from mirror_functions.py
            This contains the list of neighbors to make sure the genes don't break the mirror.
        """
        if  mirror.fits_mirror(genes): # if the genes don't break the mirror
            applied_voltages = genes * self.VOLTAGE_MULTIPLIER # multiply each gene by some mirror constant to get the voltages sent to the mirror
            voltage_array = self.__array_conversion(applied_voltages) # change the mapping of the indices
            self.__send_to_board(votlage_array[:19], voltage_array[19:])
        else:
            print("Error: Tried writing the genes to the mirror, but they would've broken it")
        return

    def __send_to_board(voltages0, voltages1):
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

    def __array_conversion(genes):
        """Maps genes to a different order so that indices in the genes array corresponds to the correct index of the mirror

        Parameters
        ----------
        genes: genes, 1D numpy array
            the genes or actuator voltages to be tested

        Returns
        -------
        mapped_genes : mapped genes, 1D numpy array
            The genes to be tested after being mapped so the index corresponds to the correct actuator
        """
        # Change the order of the genes so each index corresponds with the correct index on the deformable mirror
        mapped_genes = [genes[17], genes[31], genes[32], genes[8], genes[18], genes[9], genes[1], genes[16], genes[0], genes[23],
                        genes[6], genes[21], genes[20], genes[19], genes[33], genes[22], genes[7], genes[10], genes[5], genes[29],
                        genes[27], genes[26], genes[28], genes[14], genes[35], genes[24], genes[36], genes[34], genes[11], genes[3],
                        genes[2], genes[15], genes[4], genes[25], genes[30], genes[13], genes[12]]
        return mapped_genes


class USB_DM_comm(object):
    def __init__(self):
        self.voltage_multiplier = 13.72

        directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path

        LabVIEW = win32com.client.Dispatch("Labview.Application")   # Start running Labview
        self.usbVI = LabVIEW.getvireference(directory_path + '\\Volt_to_mirror_2.vi')    # path to the LabVIEW VI for the first board
        self.usbVI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path

    def write_to_mirror(genes, mirror):
        """Checks whether the voltage values satisfy the requirements then sends them to the deformable mirror
        Parameters
        ----------
        genes: genes, 1D numpy array
            the genes or actuator voltages to be tested
        mirror : object from mirror_functions.py
            This contains the list of neighbors to make sure the genes don't break the mirror.
        """
        if mirror.fits_mirror(genes): # if the genes don't break the mirror
            voltages = genes * self.voltage_multiplier  # multiply each of the genes so that the actuators get the correct voltage
            self.__send_to_board(voltages)
        else:
            print("Error: Tried writing the genes to the mirror, but they would've broken it")

    def __send_to_board(voltages):
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
       

if __name__ == "__main__":
    print('You meant to run GeneticAlgorithm.py')

