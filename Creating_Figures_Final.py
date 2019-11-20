# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 12:11:23 2019

@author: byron
"""

import numpy as np                 #for performing and matrix calculations           #for masking values in arrays
import matplotlib.pyplot as plt    #for plotting/visualizing
from datetime import datetime      #for date and time handling  
import geopandas as gpd            #for reading in the shapefiles

# Function to read in the inputs
def get_inputs(file):
    
    points_file = str(file)
    
    if not ((points_file.endswith(".csv")) or (points_file.endswith(".shp"))):

        raise IOError(points_file)

    points = gpd.read_file(points_file)
    
    return points

# Function to assign date-time properties to each index date.
def correct_names(data_frame):
    for head in data_frame:
  
        if head.startswith('S_'):
            new_head = head + '0626'
            new_head = new_head.replace('Red', 'RED')
            data_frame.rename(columns = {head: new_head}, inplace= True)

        # Remove inexplicable ..._m columns, and columns that represent the mean 
        # of two or more dates:
        elif 'Red' in head:
            new_head = head.replace('Red', 'RED')
            data_frame.rename(columns = {head: new_head}, inplace= True)
        
        elif head.startswith('SWIR2'):
            new_head = 'SWIR' + head[5:9]
            data_frame.rename(columns = {head: new_head}, inplace= True)
            
        elif head.endswith('_m'):
            data_frame = data_frame.drop(columns = head)
        
        elif head.endswith('min'):
            data_frame = data_frame.drop(columns = head)
        
        elif head.endswith('_'):
            data_frame = data_frame.drop(columns = head)
        
        elif head.endswith('_1'):
            data_frame = data_frame.drop(columns = head)
        
        elif not "0" in head:
            data_frame = data_frame.drop(columns = head)
    
    return(data_frame)

# Function to turn shapefiles into dictionaries, then create a new dictionary that 
# has keys for each column (index_date) and avg, min, max, quantiles as values.
def create_stat_dictionary(data_frame):
    dictionary = data_frame.to_dict()
    for key in dictionary.keys():
        
        if key != 'geometry':
            array = np.array(list(dictionary[key].values()),dtype = np.float64)
            array = array[np.logical_not(np.isnan(array))]
            array1 = np.ma.masked_less(array,-9990)
            mean = np.mean(array1)
            q1 = np.quantile(array1, 0.1)
            q3 = np.quantile(array1, 0.9)
            _min = np.ma.min(array1)
            _max = np.max(array1)
            dictionary[key] = [mean, _min, _max, q1, q3]
    
    return(dictionary)

# Function to create and assign dates to index_date names

# Function to sort the index_date names by date
def assign_date(_list):
    # Find and point to the location in the string where 4 numbers are together

    place_list = []
    for x, c in enumerate(_list):
        if c.isdigit():
            place = int(x)
            place_list.append(place)
            
    start = place_list[0]
    
    datestring = (_list[(start):(start+4)])
    
    dates = '{:%m-%d}'.format(datetime.strptime(datestring, '%m%d'))
    
    return(dates)

# Function to find all keys that contain index name, then create a list that contains
# the associated mean vals, min vals, etc.
def create_chart(dictionary, index, color):
    name_list = []
    mean_list = []
    min_list = []
    max_list = []
    q1_list = []
    q3_list = []

    for key in dictionary:
        if index in key:
            mean = dictionary[key][0]
            _min = dictionary[key][1]
            _max = dictionary[key][2]
            q1 = dictionary[key][3]
            q3 = dictionary[key][4]
            mean_list.append(mean)
            min_list.append(_min)
            max_list.append(_max)
            q1_list.append(q1)
            q3_list.append(q3)
            name_list.append(key)
    
    dated_list = list(map(assign_date, name_list)) 
    mean_sorted = sorted(list(zip(dated_list, mean_list)))
    mean_sorted = list(zip(*mean_sorted))
    
    min_sorted = sorted(list(zip(dated_list, min_list)))
    min_sorted = list(zip(*min_sorted))
    
    max_sorted = sorted(list(zip(dated_list, max_list)))
    max_sorted = list(zip(*max_sorted))    
    
    q1_sorted = sorted(list(zip(dated_list, q1_list)))
    q1_sorted = list(zip(*q1_sorted))   
    
    q3_sorted = sorted(list(zip(dated_list, q3_list)))
    q3_sorted = list(zip(*q3_sorted)) 
    
    plt.plot(mean_sorted[0], mean_sorted[1], color + 'o-')
    plt.plot(min_sorted[0], min_sorted[1], color + '+')
    plt.plot(max_sorted[0], max_sorted[1], color + '+')
    plt.plot(q1_sorted[0], q1_sorted[1], color, linestyle = 'dotted')
    plt.plot(q3_sorted[0], q3_sorted[1], color, linestyle = 'dotted')
    
def main(pres_file, abs_file, index):
    
    # Create Data frames
    pres_dframe = get_inputs(pres_file)
    abs_dframe = get_inputs(abs_file)
    #print(pres_dframe["S_Red"])
    
    pres_dframe = correct_names(pres_dframe)
    abs_dframe = correct_names(abs_dframe)

    #Get dictionary of stats per key for the dictionary
    pres_dict = create_stat_dictionary(pres_dframe)
    abs_dict = create_stat_dictionary(abs_dframe)
    
    # Apply function to create corresponding index_date and metric lists
    plt.figure(figsize=(20,8))
    plt.title('Mean, Min, Max, and 10th and 90th percentiles for ' + index, fontsize=24)
    Pres_chart = create_chart(pres_dict, index, 'b')
    Abs_chart = create_chart(abs_dict, index, 'r')
    plt.legend(['Mean for pts with >= 40% cheatgrass', 'Min', 'Max', '90th percentile', '10th percentile', 'Mean for pts with < 40% cheatgrass'])
    #plt.savefig(index+ '.png')
    
#Apply the function inputting presence points, absence points, and the desired index to examine  
main('MergedDataset_1_pres.shp', 'MergedDataset_1_abs.shp', 'TCW')
        