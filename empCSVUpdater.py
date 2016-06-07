"""
Script to incrementally check the person_dim table for new hires/contractors.  This could be used
to populate an empty person_dim table (rewrite uses a once-populated list to avoid lots of round trips
to the db, so this is not horribly inefficient now).

Note that this only incrementally adds employees - departed staff are left in the person_dim table
as there will be referencing fact table rows.

File should contain a single header row that is skipped (see skipHeader flag)
Column order in the file should match the table definition:

ID (employee ID)
First name
Last name
Employee Type (e.g. "Employee", "Contractor", etc)
Position (e.g. "SFD 3", "BA 3", "PM 4")

This is the current structure as exported from Replicon (get the report name)
"""


import psycopg2
import string
import logging
import csv
import uniDWUtils

gCommitBoundary = 100


#########################################################
# grab a list of all person IDs (employee IDs) in the
# person_dim table.  return the list
#
def getPersonList(conn):

    list = None
    try:
        cursor = conn.cursor()
    except Exception as ex:
        logging.error('failed to get cursor: ' + str(ex))
        return list

    try:
        cursor.execute('select person_id from unicon_dw.person_dim')
        r = cursor.fetchall()
        list = []
        for i in r:
            list.append(i[0])
            
    except Exception as ex:
        logging.error('failed to get list of person IDs: ' + str(ex))

    cursor.close
    return list

#########################################################
# scan the input file, determine if a given file entry is missing from the person_dim
# table, and issue an insert if necessary.
# Returns the number of employees added to the person_dim table
#
def updateEmps(conn, personList, file):

    rowCount = 0
    insertCount = 0
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

            id = int(values[0].replace("'", "''"))
            #if the person isn't already in (based on employee ID), insert 'em, otherwise, continue to next entry
            if not (id in personList):
                #note strip off newline char of the last value, escape single quotes
                insertStmt = 'insert into unicon_dw.person_dim(person_id, first_name, last_name, position, employee_type) ' + \
                             "values (%s, '%s', '%s', '%s', '%s')" % (values[0].replace("'", "''"), values[1].replace("'", "''"), values[2].replace("'", "''"), values[3].replace("'", "''"), values[4].replace("'", "''").rstrip('\r\n'))
                logging.debug(insertStmt)
                cursor.execute(insertStmt)
                insertCount += 1
                if(insertCount%gCommitBoundary == 0):
                    conn.commit()
                    logging.debug('Committed ' + str(gCommitBoundary))
            
    except Exception as ex:
        logging.error('Failed in row processing at line ' + str(rowCount) + ' ex: ' + str(ex))
        conn.rollback()  #note: may not rollback everything!
        cursor.close()
        return insertCount

    conn.commit()
    cursor.close()
    
    return insertCount

#########################################################
# main script
#

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
connection=None
inputFile = None

try:
    logging.info('Starting emp updater.')
    
    # read config file
    config = uniDWUtils.getConfig('config.cfg')    
    logging.debug('emp updater Config: ' + str(config))
    
    # open csv file
    filename = config['empcsvfilename']
    inputFile = uniDWUtils.getFile(filename)
    if (inputFile == None):
        logging.fatal('emp updater Failed to open file ' + filename)
        exit(-1)
    
    logging.debug('emp updater Input CSV file opened.')
    
    connection = uniDWUtils.getConnection(config)
    if connection == None:
        logging.fatal("emp updater failed to get db connection.  exiting")
        exit(-1)
    logging.debug('emp updater Got db connection')

    # get a list of existing persons/employees
    persList = getPersonList(connection)
    logging.debug('emp updater Existing person list, len=' + str(len(persList)) + ' list=' + str(persList))
    
    # scan the input CSV file, compare to existing entries, insert as necessary
    c = updateEmps(connection, persList, inputFile)
    logging.debug('emp updater Updates finished.  Inserted ' + str(c) + ' rows.');
    
except Exception as ex:
    logging.fatal('emp updater Failed with exception: ' + str(ex))

logging.debug('emp updater Cleaning up.')
if(connection != None): connection.close()
if(inputFile != None): inputFile.close()
logging.info('emp updater done.')
