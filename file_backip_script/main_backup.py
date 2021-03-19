#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import shutil
import subprocess
import time
import datetime
import os.path  #for py2
#import pathlib #for py3
import sys
import config
import socket
import fcntl
import struct
from logger import Logger

today = str(datetime.date.today())
logger = Logger("backup.log")


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def creat_dir(filepath):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        logger.log("INFO", + filepath + " dir is exist")


def pre_backup():
    logger.log("INFO", "Starting Pre_backup...")
    logger.log("INFO", "Pre_backup task1 checking log dir")

    logDir = os.system("cd " + config.log_dir)
    try:
        if logDir != 0:
            creat_dir(config.log_dir)
    except:
        logger.log("ERROR", "Pre_backup task1 An exception occurred")
        sys.exit(1)
    else:
        logger.log("SUCCESS", "Pre_backup task1 log dir is exist")

    logger.log("INFO", "Pre_backup task2 checking daily dir")
    dirCheck = os.system("cd " + config.local_mount + '/' + str(get_ip_address(config.local_interface)) )
    try:
        if dirCheck != 0:
            creat_dir(config.local_mount + '/' + str(get_ip_address(config.local_interface)) + '/' + str(today) + '/') #最後要留/才會跟著建立dir
            logger.log("SUCCESS", "Pre_backup task2 successfully")
    except:
        logger.log("ERROR", "Pre_backup task2 An exception occurred")
        sys.exit(1)
    else:
        creat_dir(config.local_mount + '/' + str(get_ip_address(config.local_interface)) + '/' + str(today) + '/')
        logger.log("SUCCESS", "Pre_backup task2 creat daily dir successfully")


def backup():
    logger.log("INFO", "Starting backup to " + str(local_backup_dir)  + " directories...")
    if os.path.isdir(str(local_backup_dir)):
        for var in config.backup_list:
            try:
                if os.path.isfile(var):#如果是檔案
                    logger.log("INFO", "Starting backup file " + var)
                    status = os.system("cd " + str(local_backup_dir) + " && rsync -ahR " + var + ' .')
                    if status == 0:
                        logger.log("SUCCESS", "Backup file "+ var +" successfully")
                    else:
                        logger.log("ERROR", "Failed to backup "+ var)
                elif os.path.isdir(var): #如果是資料夾
                    logger.log("INFO", "Starting backup dir " + var)
                    status = os.system("cd " + str(local_backup_dir) + " && rsync -ahR " + var + ' .')
                    if status == 0:
                        logger.log("SUCCESS", "Backup dir "+ var +" successfully")
                    else:
                        logger.log("ERROR", "Failed to backup "+ var)
                else:
                        logger.log("ERROR", var + " not exist .Please check config.py file")
            except:
                logger.log("ERROR", "An exception occurred")
                sys.exit(1)
    else:
        logger.log("ERROR", "No directories to backup")
        sys.exit(1)


def rsyncBackups():
    logger.log("INFO", "Starting sync to remote dir...")
    try:
        #sendCheck = subprocess.call(["rsync", "-avh", str(local_backup_dir) + ' ' + config.cloud_user + '@' + config.cloud_ip + ':' + config.cloud_mount + '/' + str(get_ip_address(config.local_interface)) + '/'])
        subprocess.call(["rsync", "-avh", str(local_backup_dir) + ' ' + config.cloud_user + '@' + config.cloud_ip + ':' + config.cloud_mount + '/' + str(get_ip_address(config.local_interface)) + '/'])
    except OSError as e:
        print(e.output)
        logger.log("ERROR", "rsync to remote task An exception occurred")
        sys.exit(1)
    else:
        logger.log("SUCCESS", "Successfully rsync to remote dir")


init_check = (config.local_mount + '/' + str(get_ip_address(config.local_interface)) + '/' + today)
local_backup_dir = str(config.local_mount + '/' + str(get_ip_address(config.local_interface)) + '/' + today)
#try:
if os.path.exists(init_check):
    shutil.rmtree(config.local_mount + '/' + str(get_ip_address(config.local_interface)) + '/' + today)
    pre_backup()
    backup()
    rsyncBackups()
else:
    pre_backup()
    backup()
    rsyncBackups()
#except:
#    logger.log("ERROR", "init_check An exception occurred")
