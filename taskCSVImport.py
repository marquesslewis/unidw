"""
Script to import CSV file of timecard entries.  This is an initial rev just to populate some sample data.
A full version will need to ensure that deltas can be brought in and ensure no duplicate entries.

A somewhat naive lookup table is built from the person and time dimension tables.  Due to the size of the task table,
this is not pulled into a dictionary and queries are executed to determine each of the task dim IDs needed.  A cache approach could be used
as there are likely repeated uses of a given task each time period.

"""


import psycopg2
import string
import logging
import csv
from uniDWUtils import getConfig, getFile, getConnection

gCommitBoundary = 50

#########################################################
# insert the task rows
# Note - rewrite this to use the psycopg2 copy statement to bulk load the file
#
def insertTimeCardEntries(conn, file):

    rowCount = 0
    global gCommitBoundary
    
    try:
        cursor = conn.cursor()
    except Exception as ex:
        logging.error('failed to get cursor: ' + str(ex))
        return rowCount
    
    try:
        logging.debug('starting row processing')
        file.readline() #skip the header row
        reader = csv.reader(file, delimiter=',', quotechar='"')
        for values in reader:
            rowCount += 1  #also used as the task_id for now.  barf
            logging.debug(values)
            
            
    except Exception as ex:
        logging.error('Failed in row processing at line ' + str(rowCount) + ' ex: ' + str(ex))
        conn.rollback()  #note: may not rollback everything!
        cursor.close()
        return rowCount

    try:
        cursor.execute('select count(*) from unicon_dw.timecard_entry_fact')
        r = cursor.fetchone()
        logging.debug('timecard_entry_fact table row count: ' + str(r[0]))
    except Exception as ex:
        logging.error('Failed counting rows in timecard_entry_fact' + str(ex))
        
    conn.commit()
    cursor.close()
    
    return rowCount

#########################################################
# main script
#

connection=None

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)



try:
    logging.info('Starting timecard importer.')
    
    # read config file
    config = getConfig('config.cfg')    
    
    # open csv file
    inputFile = getFile(config['timecardcsvfilename'])
    if (inputFile == None):
        logging.fatal('Failed to open file ' + config['timeCardCSVFileName'])
        exit(-1)
    
    logging.debug('Input CSV file opened.')
    
    # get db connection
    connection = getConnection(config)
    if (connection == None):
        logging.fatal('Failed to connect to db. ')
        exit(-1)
    logging.debug('Got db connection')

    #build map table of employees and IDs
    #build map of time dimension
    #get cache thingie for task IDs given names
    
    c = insertTimeCardEntries(connection, inputFile)
    logging.info('Inserts finished.  Inserted ' + str(c) + ' rows.');
    
except Exception as ex:
    logging.fatal('Failed in main importer with exception: ' + str(ex))

logging.debug('Cleaning up.')
if(connection != None): connection.close()
if(inputFile != None): inputFile.close()
logging.info('Task importer done.')
