#!/usr/bin/env python
#coding=utf8
#========================================
# LIS3DH data logging script
# Created by Max Dukov
# based on MMA8451.py - Python API for MMA8451 accelerometer.  Author: jatin kataria
# maxdukov@gmail.com
#========================================
# 

print "LIS3DH data collection script v1.0.01062017"

import os
import sqlite3
import LIS3DH
import time, datetime, spidev, sys, smbus

#import argparse
#import sched


#==============================
# SQLite setup
#==============================
# init sqlite connection
con = sqlite3.connect('/var/www/html/gyro.db')
cur = con.cursor()

#============================================
# check and create tables, if it's not exists
#============================================
# cur.execute('DROP TABLE log') 
# cur.execute('DROP TABLE archive')
cur.execute('CREATE TABLE IF NOT EXISTS log_lis     ( dt VARCHAR(30), id INT, x INT, y INT, z INT, temp INT, norm BOOLEAN default 0)')
cur.execute('CREATE TABLE IF NOT EXISTS archive_lis ( dt VARCHAR(30), id INT, x INT, y INT, z INT, temp INT, norm BOOLEAN default 0, uploaded BOOLEAN default 0)')
cur.execute('CREATE INDEX IF NOT EXISTS upld ON archive_lis(uploaded)')
cur.execute('DELETE FROM log_lis')
con.commit()


if __name__ == "__main__":
    # let's init accelerometr
    accel = LIS3DH.Accelerometer('i2c',i2cAddress = 0x18)
    accel.set_ODR(odr=400, powerMode='normal')
    accel.axis_enable(x='on',y='on',z='on')
    accel.interrupt_high_low('high')
    accel.latch_interrupt('on')
    accel.set_BDU('on')
    accel.set_scale()
    accel.enable_temperature()
    size = 400*3
    dt_list = [0]*size
    x_list = [0]*size
    y_list = [0]*size
    z_list = [0]*size
    t_list = [0]*size
    t = 0
    start = datetime.datetime.now()
    run = datetime.datetime.now()
    print '=== Sensor settings:'
    print '==> Range = 2G'
    print '==> Data rate = 400Hz'
    print '==> Resolution = High(12-bit)'
    print '============================='
    print '=== data collection started. Start time='+str(run)
    while t < size:
    	if (run + datetime.timedelta(0,0,2490))  <= datetime.datetime.now():
        	run = datetime.datetime.now()
                dt_list[t] = run
	        x_list[t] = accel.x_axis_reading()*2/4096
                y_list[t] = accel.y_axis_reading()*2/4096
                z_list[t] = accel.z_axis_reading()*2/4096
                t_list[t] = accel.get_temperature()
	        t = t+1
    print '=== data collection finished, start data saving. End time='+str(run)
    t = 0
    while t < size:
    	cur.execute('INSERT INTO log_lis     (dt, x, y, z, temp ) VALUES(?, ?, ?, ?, ?)',(dt_list[t], x_list[t], y_list[t], z_list[t], t_list[t]))
        cur.execute('INSERT INTO archive_lis (dt, x, y, z, temp ) VALUES(?, ?, ?, ?, ?)',(dt_list[t], x_list[t], y_list[t], z_list[t], t_list[t]))
        t = t+1
    con.commit()
    con.close
    print '=== data saving finished, data visualisation starting'
    cmd = "./fft.py "
    os.system(cmd)
