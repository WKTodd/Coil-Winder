#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 13:58:28 2021

@author: bill
"""

from serial.tools import list_ports

ports = list_ports.comports()

for port in ports:
    
    print(port)
    
        
