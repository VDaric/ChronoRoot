#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 10:42:58 2020

@author: ncaggion
"""

from graph.fileFunc import download_file_from_google_drive
from zipfile import ZipFile
import pathlib
import os

file_id = '1eVVbWqPUjwYCONeUmx-5nq1wyanhXcTh'
destination = os.path.join(pathlib.Path().absolute(),'modelWeights.zip')

print('Downloading model weights from Google Drive')

download_file_from_google_drive(file_id, destination)

print('Extracting model weights')

with ZipFile('modelWeights.zip', 'r') as zipObj:
   # Extract all the contents of zip file in current directory
   zipObj.extractall()

try:
    os.remove(destination)
except:
    pass
  
print('Extraction finished')
