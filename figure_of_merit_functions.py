'''
Created on Wed March 28 2018

@author Yong Ma, yongm@umich.edu
'''

#from pyicic.IC_ImagingControl import *
import numpy as np 
import matplotlib.pyplot as plt
import copy

import matplotlib.cm as cm

def pico_FOM(dataA, fom_num):
    if fom_num == "test":   # if the daq device is being tested
        print (np.absolute(dataA).mean())
        return
    return np.absolute(dataA).mean()
    

def rgb2gray(rgb):
	'''Convert the 3-channel rgb image into grayscale
	'''
	r, g, b = rgb[:,:,0] , rgb[:,:,1] , rgb[:,:,2]
	gray  = 0.2989 * r + 0.587 * g + 0.114 * b
	return gray


def ic_FOM(frameout, fom_num):
    
    imgray = rgb2gray(frameout) # convert rgb image into grayscale
    if fom_num == "test":   # if the daq device is being tested
        plt.imshow(frameout,cmap=plt.get_cmap('gray'))
        plt.colorbar()
        plt.show()
        #plt.savefig('//IC//test.png')
        return
    
    satu = imgray[imgray>254].shape[0]
    plt.imsave('figure_of_merit.png', frameout, cmap=cm.gray)
    if satu > 0:
    	print('Image saturated with %d pixels'%satu)
    	return 0
    else:
    	if fom_num == 1:
    		#FOM 1
    		I = abs(imgray)**2
    		x = np.arange(imgray.shape[1]).astype(float)
    		y = np.arange(imgray.shape[0]).astype(float)
    		mu0 = np.trapz(np.trapz(I, x ),y)
    		mean_x = np.trapz(np.trapz(I * x, x), y)/mu0
    		mean_y = np.trapz(np.trapz(I, x)*y, y)/mu0
    		r0 = 50
    		X, Y= np.meshgrid(x,y)
    		r = (Y - mean_y)**2 + (X - mean_x)**2
    		fom = (1-np.sum(imgray[r>=r0**2]) / np.sum(imgray) ) * np.sum(imgray[r<r0**2])
    		y_peak, x_peak = np.unravel_index(imgray.argmax(), imgray.shape) # find the target position for FOM calculation, here the maximum point is the target position
    
    	elif fom_num == 2:
    		#FOM2 (Image Moment)
    		x_peak = 520
    		y_peak = 554
    		xx = np.arange(imgray.shape[1]).astype(float)
    		yy = np.arange(imgray.shape[0]).astype(float)
    		X, Y= np.meshgrid(xx,yy)
    		d1 = (Y - y_peak)**2
    		d2 = (X - x_peak)**2
    		d = (d1+d2)**4
    		d[y_peak,x_peak]=1
    		fom = imgray / d
    		fom[y_peak,x_peak]=0
    		fom = np.sum(fom)
    
    	elif fom_num == 3:
    		#FOM3
    		fom = np.sum(imgray**2);
    
    	elif fom_num == 4:
    		#FOM4
    		fom = np.sum(imgray);
    
    	print(frameout.max(), fom)
    	return fom
    
def NI_DAQ_FOM(voltage, fom_num):
    """This is the figure of merit function for the NI_DAQ single voltage hardware
    
    Parameters
    ----------
    voltage: voltage, variable type unknown -> maybe float
        the averaged voltage read by the NI DAQ hardware
    fom_num : figure of merit number, integer
        This determines which figure of merit function to run
    
    Returns
    -------
    figure_of_merit: figure_of_merit, variable type unknown -> maybe float
        the measure of how good the mirror shape achieved a desired goal
    """
    if fom_num == "test":   # if the daq device is being tested
        print(voltage)  
        return
    
    # Return the positive voltage
    if fom_num == 1:
    	return voltage
    
    #Return the negative voltage
    elif fom_num == 2:
    	return -voltage
    
def Andor_FOM(image, fom_num):
    if fom_num == "test":   # if the daq device is being tested
        plt.imshow(image,cmap=plt.get_cmap('gray')) # plot the image
        plt.colorbar()
        plt.show()
        #plt.savefig('//Andor//test.png')
        return
    