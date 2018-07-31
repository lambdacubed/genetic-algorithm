#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains functions which determine the figure of merit for each
data acquisition device available.

"""

from pyicic.IC_ImagingControl import *
import numpy as np 
import matplotlib.pyplot as plt
import copy

import matplotlib.cm as cm

def pico_FOM(data, fom_num):
    """
    Calculate the figure of merit for the picoscope.

    ...

    Parameters
    ----------
    data : array
        The data from the picoscope
    fom_num : int
        The figure of merit calculation you'd like to use.

    Returns
    -------
    int, float
        Figure of merit of picoscope data.

    """
    if fom_num == "test":   # if the daq device is being tested
        plt.plot(data)
        plt.xlabel("Sample number")
        plt.title("Signal")
        return
    return np.absolute(data).mean()
    

def rgb2gray(rgb):
	'''Convert the 3-channel rgb image into grayscale
	'''
	r, g, b = rgb[:,:,0] , rgb[:,:,1] , rgb[:,:,2]
	gray  = 0.2989 * r + 0.587 * g + 0.114 * b
	return gray


def ic_FOM(frameout, fom_num):
    """
    Calculate the figure of merit for the imaging source cameras.

    ...

    Parameters
    ----------
    frameout : array
        The image in a numpy array
    fom_num : int
        The figure of merit calculation you'd like to use.

    Returns
    -------
    int, float
        Figure of merit of IC image.

    """
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
    """
    Calculate the figure of merit for the NI DAQ.

    ...

    Parameters
    ----------
    voltage: maybe float
        the averaged voltage read by the NI DAQ hardware
    fom_num : int
        The figure of merit calculation you'd like to use.

    Returns
    -------
    float
        Figure of merit of NI DAQ voltage.

    """
    if fom_num == "test":   # if the daq device is being tested
        print(voltage)  
        return
    
    if fom_num == 1:
    	return voltage  # Return the positive voltage
    elif fom_num == 2:
    	return -voltage # Return the negative voltage
    
def Andor_FOM(image, fom_num):
    """
    Calculate the figure of merit for the Andor camera.

    ...

    Parameters
    ----------
    image : array
        The image captured by the Andor camera in a numpy array
    fom_num : int
        The figure of merit calculation you'd like to use.

    Returns
    -------
    float
        Figure of merit of Andor image.

    """
    if fom_num == "test":   # if the daq device is being tested
        plt.imshow(image,cmap=plt.get_cmap('gray')) # plot the image
        plt.colorbar()
        plt.show()
        #plt.savefig('//Andor//test.png')
        return
    
    if fom_num == 1 or fom_num == 2:
        total = np.sum(image)
        print(total)
        fom = total
        return fom  # return the sum of the image