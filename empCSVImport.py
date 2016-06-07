"""
Script to import CSV file of employees into the person_dim table.

File should contain a single header row that is skipped (see skipHeader flag)
Column order in the file should match the table definition:

ID (employee ID)
First name
Last name
Employee Type (e.g. "Employee", "Contractor", etc)
Position (e.g. "SFD 3", "BA 3", "PM 4")


"""


import psycopg2
import string
import logging
import csv
import uniDWUtils

gCommitBoundary = 100


#########################################################
# insert the employee rows.
# Note - rewrite this to use the psycopg2 copy statement to bulk load the file
#
def insertEmps(conn, file):

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
        for values  in reader:
            rowCount += 1
            logging.debug(values)

            #note strip off newline char of the last value, escape single quotes
            insertStmt = 'insert into unicon_dw.person_dim(person_id, first_name, last_name, position, employee_type) ' + \
                         "values (%s, '%s', '%s', '%s', '%s')" % (values[0].replace("'", "''"), values[1].replace("'", "''"), values[2].replace("'", "''"), values[3].replace("'", "''"), values[4].replace("'", "''").rstrip('\r\n'))
            logging.debug(insertStmt)
            cursor.execute(insertStmt)
            if(rowCount%gCommitBoundary == 0):
                conn.commit()
                logging.debug('Committed ' + str(gCommitBoundary))
            
    except Exception as ex:
        logging.error('Failed in row processing at line ' + str(rowCount) + ' ex: ' + str(ex))
        conn.rollback()  #note: may not rollback everything!
        cursor.close()
        return rowCount

    conn.commit()
    cursor.close()
    
    return rowCount

#########################################################
# main script
#

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
connection=None
inputFile = None

try:
    logging.info('Starting emp importer.')
    
    # read config file
    config = uniDWUtils.getConfig('config.cfg')    
    logging.debug('Config: ' + str(config))
    
    # open csv file
    filename = config['empcsvfilename']
    inputFile = uniDWUtils.getFile(filename)
    if (inputFile == None):
        logging.fatal('Failed to open file ' + filename)
        exit(-1)
    
    logging.debug('Input CSV file opened.')
    
    connection = uniDWUtils.getConnection(config)
    logging.debug('Got db connection')

    c = insertEmps(connection, inputFile)
    logging.debug('Inserts finished.  Inserted ' + str(c) + ' rows.');
    
except Exception as ex:
    logging.fatal('Failed in main importer with exception: ' + str(ex))

logging.debug('Cleaning up.')
if(connection != None): connection.close()
if(inputFile != None): inputFile.close()
logging.info('Emp importer done.')
