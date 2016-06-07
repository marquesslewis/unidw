#########################################################
# Utilities for the Unicon Data warehouse Importer
#

import logging
import ConfigParser
import psycopg2


#########################################################
# read config file, return config dictionary
#
def getConfig(filename):
    config = {}
    try:
        parser = ConfigParser.ConfigParser()
        parser.read(filename)
        itemList = parser.items('Main')
        for i in itemList:
            config[i[0]] = i[1]
            
        logging.debug("Loaded config: \n\n" + str(config) + "\n\n")
        
    except Exception as err:
        logging.error('failed to load config ' + str(err))

    return config



#########################################################
# open and return the input file, in read mode
#
def getFile(filename):
    try:
        f = open(filename, 'r')
    except Exception as ex:
        logging.error('Failed to open file: ' + filename + ' : ' + str(ex))
        return None
    return f

#########################################################
# get a Postgres db connection (works for Redshift)
#
def getConnection(config):
    conn = None
    try:
        conn=psycopg2.connect(dbname=config['dbname'], host=config['host'], port=eval(config['port']), user=config['user'],  password=config['password'])
    except Exception as err:
        logging.error('failed to get DB connection to: ' + config['dbname'] + "  ex: " + str(err))

    return conn
