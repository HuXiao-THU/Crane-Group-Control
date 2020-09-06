import os
import csv
import queue

def loadData(file_path='data/crane_data.csv'):
    """
    load data, from crane_data.csv as default
    """
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for line in reader:
            buffer = []
            for item in line:
                buffer.append(int(item))
            data.append(buffer)
    return data

def loadTargetData():
    """
    load target data from target_data.csv
    """
    data = {}
    ori_data = loadData('./data/target_data.csv')
    for line in ori_data:
        ID = line[0]
        if ID not in data.keys():
            data[ID] = queue.Queue()
            data[ID].put(line)
        else:
            data[ID].put(line)
    return data