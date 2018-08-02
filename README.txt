This is a genetic algorithm used for machine learning. It is a black-box optimization technique originally 
developed by O. Albert and was published in Optics Letters, Vol. 25, No. 15, August 1, 2000. It was then 
moved to python with some improvements written by Mark Mathis markmath@umich.edu.



HOW TO RUN
1) Open command prompt by pressing the windows key and typing "command prompt"
2) Navigate to the folder which contains GeneticAlgorithm.py (by using the "cd" and "dir" commands)
3) Type "python GeneticAlgorithm.py"


INITIALIZATION SETTINGS
Change the default values of the genetic algorithm in genetic_algorithm.ini


DATA ACQUISITION SETTINGS
To adjust data acquisition settings, navigate to the appropriate folder and adjust the properties.ini file
For example, navigate to "Andor/Andor properties.ini" and adjust those initialization settings.

Note: the program always searches for the highest figure of merit.
If you want to optimize for the smallest value just make your figure of merit negative 


HOW TO TEST A DATA ACQUISITION DEVICE
Simply run data_acquisition_functions.py


HOW TO SEND VOLTAGES TO THE MIRROR OR TEST INDIVIDUAL ACTUATORS
Simply run Set_voltages.py


HOW TO SET UP A NEW DATA ACQUISITION DEVICE
1) Create a folder for your new device 
2) Within that folder, create a properties.ini file formatted the same as the other .ini files.
3) Adjust the data_acquisition_devices.py file to include an class for your device with an __init__, acquire, figure of merit, and shut_down function.
4) Include your device as an available option in the genetic_algorithm.ini file, in DAQ_DEVICES, and in initialize_daq_device() in data_acquisition_devices.py

Example: If you want to call your device "device1", create a folder named "device1". Within that folder, create
a file named "device1 properties.ini". Adjust data_acquisition_devices.py to have an option for 
"elif (self.device == DAQ_DEVICES[{insert index of "device1" in DAQ_DEVICES}]):" and have it return the device1 class.
Then, go into genetic_algorithm.ini and let "device1" be an option.
Note: the device name "device1" or whatever you choose, cannot have any space in it





