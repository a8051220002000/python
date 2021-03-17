#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import shutil
import time
import datetime
import pathlib
import sys
import config
from logger import Logger

today = str(datetime.date.today())
logger = Logger("backup.log")



def pre_backup():
    logger.log("INFO", "Starting Pre_backup...")
    dirCheck = os.system("cd " + config.cloud_mount)
    if dirCheck != 0:
        createBackup = pathlib.Path(config.cloud_mount).mkdir(parents=True, exist_ok=True)
        if createBackup == 0:
            os.system("cd " + config.cloud_mount + " && mkdir " + str(today) )
            logger.log("SUCCESS", " Pre_backup successfully created dir")
        else:
            logger.log("ERROR", " Pre_backup failed created dir")
            sys.exit(1)
    else:
        os.system("cd " + config.cloud_mount + " && mkdir " + str(today) )
        logger.log("SUCCESS", " Pre_backup successfully created directory")


def backup():
    logger.log("INFO", "Starting backup to " + str(config.cloud_mount + '/' + today) + " directories...")
    if os.path.isdir(str(config.cloud_mount + '/' + today )):
        for var in config.backup_list:
            try:
                if os.path.isfile(var):#如果是檔案
                    logger.log("INFO", "Starting backup file " + var)
                    status = os.system("cd " + config.cloud_mount + '/' + today + " && rsync -avhR " + var + ' .')
                    if status == 0:
                        logger.log("SUCCESS", "Backup file "+ var +" successfully")
                    else:
                        logger.log("ERROR", "Failed to backup "+ var)
                elif os.path.isdir(var): #如果是資料夾
                    logger.log("INFO", "Starting backup dir " + var)
                    status = os.system("cd " + config.cloud_mount + '/' + today + " && rsync -avhR " + var + ' .')
                    if status == 0:
                        logger.log("SUCCESS", "Backup dir "+ var +" successfully")
                    else:
                        logger.log("ERROR", "Failed to backup "+ var)
                else:
                        logger.log("ERROR", var + " not exist this dir or file backup failed.Please check it!")
            except:
                logger.log("ERROR", "An exception occurred")
                sys.exit(1)
    else:
        logger.log("ERROR", "No directories to backup")
        sys.exit(1)



def rsyncBackups():
    logger.log("INFO", "Starting rsync to remote backup dir...")
    for file in os.listdir(config.cloud_mount):
        if os.path.isfile(file):
            os.remove(file)
        elif os.path.isdir(file):
            os.rmdir(file)
        else:
            logger.log("ERROR", file + " can't be deleted!")
    logger.log("SUCCESS", " Successfully deleted old backup files")



if os.path.exists(config.cloud_mount + '/' + today):
    shutil.rmtree(config.cloud_mount + '/' + today)
    pre_backup()
    backup()
    #rsyncBackups()
elif os.path.exists(config.cloud_mount):
    pre_backup()
    backup()
    #rsyncBackups()
else:
    logger.log("ERROR", "This backup nothing to do please check backup directory")
    logger.closeFile()
    sys.exit(1)
logger.closeFile()