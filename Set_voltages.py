"""This file sets voltages on the mirror from a file, for a constant voltage, or tests
individual actuators

Functions:
send_file() -- sets voltages on the mirror from a file of actuator voltages
send_genes() -- sets constant voltages on the mirror which are determined within the function
test_actuators -- test the voltages for individual actuators
"""

import numpy as np  # general useful python library

import file_functions as file_f     # used to read from files
import mirror_communication_devices as mirror_devices
import mirrors

def send_file(mirror_comm_device, mirror):
    """ This sets voltages on the mirror from a file of actuator voltages
    """
    while True:

        print('Please input the filename contained in the ', file_f.MIRROR_VOLTAGES_FOLDER, ' folder (include .adf):')
        filename = input()
        saved_voltages = file_f.read_adf(filename, mirror.num_genes) +1.5  # read the saved voltages from the given file
        
        print('You are setting voltages for deformable mirror')
        print('Actuator voltages are: ', saved_voltages)   # show the operator what voltages they are sending to the mirror
        if mirror.fits_mirror(saved_voltages):
            mirror_comm_device.write_to_mirror(saved_voltages, mirror) # send the voltages to the mirror
        else:
            print("Voltages would've broken mirror.")

        print("Finished testing? (Enter 'y' if done and anything else if not done)")
        done = input()  # determine if the user is done
        if (done == 'y'):
            print("\nSending all 0's to the mirror")
            test_voltages = np.zeros(mirror.num_genes)    # set the actuator voltages back to 0    
            print("Voltages are: ", test_voltages)
            if mirror.fits_mirror(test_voltages):
                mirror_comm_device.write_to_mirror(test_voltages, mirror)   # write the set of voltages to the mirror
            else:
                print("Voltages would've broken mirror.")
            break


def send_genes(mirror_comm_device, mirror):
    """This sets constant voltages on the mirror which are determined within the function
    """
    num_genes = mirror.num_genes  # there are 37 mirror voltages
    while True:
        print("Enter the voltage you'd like to send to the mirror")
        while True:
            constant_voltage = float(input())
            break
        test_voltages = np.zeros(mirror.num_genes) + constant_voltage   # create array of 37 constant voltages
        print('This is the genes:\n',test_voltages)    # show the operator what the actuator voltages are
        print('You are setting voltages for deformable mirror')
        if mirror.fits_mirror(test_voltages):
            mirror_comm_device.write_to_mirror(test_voltages, mirror)  # write the voltages to the mirror
        else:
            print("Voltages would've broken mirror.")

        print("Finished testing? (Enter 'y' if done and anything else if not done)")
        done = input()  # determine if the user is done
        if (done == 'y'):
            print("\nSending all 0's to the mirror")
            test_voltages = np.zeros(mirror.num_genes)    # set the actuator voltages back to 0    
            print("Voltages are: ", test_voltages)
            if mirror.fits_mirror(test_voltages):
                mirror_comm_device.write_to_mirror(test_voltages, mirror)   # write the set of voltages to the mirror
            else:
                print("Voltages would've broken mirror.")
            break


def test_actuators(mirror_comm_device, mirror):
    while True: # test actuators until done testing
        test_voltages = np.zeros(mirror.num_genes)# + 71.5    # initialize the array of test voltages to 0

        while True: # create a while loop until the actuator to be tested is determined
            print("Which actuator would you like to test?\nEnter a integer from 0 to 36.")
            actuator_index = int(input())
            good = (actuator_index >= 0) and (actuator_index <= mirror.num_genes-1)     # make sure the actuator is within the correct range
            if good == True: # if the input was good
                print("Testing actuator ", actuator_index, "\n")
                break
            print("You didn't enter a number between 0 and", mirror.num_genes-1)

        while True:     
            print("What would you like the singular test actuator's voltage to be?")
            print("\tNote: The voltages for all of the other actuators will be 0")
            voltage = float(input())    # get the voltage from the operator
            test_voltages[actuator_index] = voltage + 1.5
            if mirror.fits_mirror(test_voltages):
                break
            else:
                print("That voltage would've broken the mirror")

        print("Voltages are: ", test_voltages)
        if mirror.fits_mirror(test_voltages):
            mirror_comm_device.write_to_mirror(test_voltages, mirror)   # write the set of voltages to the mirror
        else:
            print("Voltages would've broken mirror.")
        print("Finished testing? (Enter 'y' if done and anything else if not done)")
        done = input()  # determine if the user is done
        if (done == 'y'):
            print("\nSending all 0's to the mirror")
            test_voltages = np.zeros(mirror.num_genes)    # set the actuator voltages back to 0    
            print("Voltages are: ", test_voltages)
            if mirror.fits_mirror(test_voltages):
                mirror_comm_device.write_to_mirror(test_voltages, mirror)   # write the set of voltages to the mirror
            else:
                print("Voltages would've broken mirror.")
            break
    
    
    
    
if __name__ == "__main__":

    print('\nThese are the mirrors you can send voltages to: ')
    print(mirrors.MIRRORS)
    print("Please enter the index of the device you would like to use.")
    print("Indices go from 0 to", len(mirrors.MIRRORS)-1)
    while True:
        index = int(input())
        if ((index <= len(mirrors.MIRRORS)-1) and (index >= 0)):
            print("Using", mirrors.MIRRORS[index])
            mirror = mirrors.initialize_mirror(mirrors.MIRRORS[index])
            break
        else:
            print("You didn't enter a correct index.")


    print('\nThese are the available devices to send voltages to the mirror: ')
    print(mirror_devices.DEVICES)
    print("Please enter the index of the device you would like to use.")
    print("Indices go from 0 to", len(mirror_devices.DEVICES)-1)
    while True:
        index = int(input())
        if ((index <= len(mirror_devices.DEVICES)-1) and (index >= 0)):
            print("Using", mirror_devices.DEVICES[index])
            mirror_comm_device = mirror_devices.initialize_comm_device(mirror_devices.DEVICES[index])
            break
        else:
            print("You didn't enter a correct index.")

    print("Would you like to send a constant voltage to the mirror, send a file to the mirror, or test individual actuators?")
    print('Enter "voltage", "file", or "test" to specify which one you would like to do.')
    while True:
        set_voltage_setting = input()
        if set_voltage_setting == "voltage":
            send_genes(mirror_comm_device, mirror)
            break
        elif set_voltage_setting == "file":
            send_file(mirror_comm_device, mirror)
            break
        elif set_voltage_setting == "test":
            test_actuators(mirror_comm_device, mirror)
            break
        else:
            print("You didn't enter a valid input. Try again.")
