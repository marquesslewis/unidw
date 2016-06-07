"""
Script to import CSV file of tasks/projects/programs/clients into the task_dim table.

File should contain a single header row that is skipped (see skipHeader flag)
Column order in the file should match the table definition:

This will generate a task ID

Task Name   Project Name   Program Name   Client

"""


import psycopg2
import string
import logging
import csv
import time
import uniDWUtils
from personCache import PersonCache
from timeDimCache import TimeDimCache

gCommitBoundary = 100



#########################################################
# insert the task rows
# Note - rewrite this to use the psycopg2 copy statement to bulk load the file
# eh, well, turns out that Replicon thinks that CSV format should be like a break report with
# next client and project only having those category values and sequential rows having the same category data
#(client name, project name), well, we'll just leave those blank.
# Hence the hijinx to determine when a new client or project entry is hit
#
def insertEntries(conn, file):

    rowCount = 0
    cursor = None
    global gCommitBoundary

    # set up dimension caches/id finder thingies
    persCache = PersonCache()
    if(persCache.load(conn) < 1):
        logging.error('failed to load person data.')
        return rowCount
    logging.debug('cache of persons loaded.')
    
    # time dim cache
    timeCache = TimeDimCache()
    
    # task cache
    
    try:
        cursor = conn.cursor()
    except Exception as ex:
        logging.error('failed to get cursor: ' + str(ex))
        return rowCount
    
    try:
        logging.debug("starting row processing\n\nStill in dev mode - not actually doing anything yet\n\n")
        file.readline()  # skip the header line, although, we (sh)could actually check for the right column headings and bail out if this is the wrong type of file

        clientName = ''
        projName = ''
        
        # fire up a CSV reader to deal with embedded quotes, commas in col values, etc.
        # column values are (in order):
        # | Client Name | Proj. Name | User Name | Task Name | Entry Date | Billing Rate Name | Billing Rate Amt | Hrs Worked | Billing Currency | Billing Amt | Comments
        reader = csv.reader(file, delimiter=',', quotechar='"')
        for values in reader:
            rowCount += 1  #also used as the task_id for now.  barf
            #logging.debug(values)
            
            # deal with "break report" format of Replicon task report CSV.  Barf.
            if(values[0] != ''):
                clientName = values[0]
                logging.debug('new client: ' + clientName)

                # good grief, there is a summary row - labelled "Full Summary" in the client name col - bail out when we hit that
                if clientName == 'Full Summary' :
                    break;  # hit the end of the file - this row isn't a timesheet entry, kick out of the loop

                continue  # rest of line is blank - indicates a new client
            
            if(values[1] != ''):
                projName = values[1]
                logging.debug('    new project: ' + projName)
                continue  # rest of line is blank - indicates a new project
            
            
            # look up dimension table keys
            personID = persCache.get(values[2])
            date = time.strptime(values[4], '%d-%b-%y')
            fmtDate = time.strftime('%Y-%m-%d', date)
            logging.debug('timecard entry date is ' + values[4] + ' for pgsql: ' + fmtDate)
            timedimID = timeCache.get(conn, fmtDate) 

            # look up task dimension key

            logging.debug(clientName + ' ' + projName + ' ' + values[2] + ' ' + str(personID))
            
            #Note strip off newline char of the last value
            #insertStmt = 'insert into unicon_dw.task_dim(task_id, task_name, project_name, program_name, client_name) ' + \
            #             "values (%d, '%s', '%s', '%s', '%s')" % (rowCount, values[0].replace("'", "''"), values[1].replace("'", "''"), values[2].replace("'", "''"), values[3].replace("'", "''").rstrip('\r\n'))
            #logging.debug(insertStmt)
            #cursor.execute(insertStmt)
            if(rowCount%gCommitBoundary == 0):
                #conn.commit()
                logging.info('Committed ' + str(gCommitBoundary))
            
    except Exception as ex:
        logging.error('Failed in row processing at line ' + str(rowCount) + ' ex: ' + str(ex))
        #conn.rollback()  #note: may not rollback everything!
        cursor.close()
        return rowCount

    #conn.commit()
    cursor.close()
    
    return rowCount

#########################################################
# main script
#



logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

connection=None
inputFile=None

try:
    logging.info('Starting timesheet importer.')
    
    # read config file
    config = uniDWUtils.getConfig('config.cfg')    
    logging.debug('Config: ' + str(config))
    
    # open csv file
    filename= config['timecardcsvfilename']
    logging.debug('Reading timesheet rows from CSV file ' + filename)
    inputFile = uniDWUtils.getFile(filename)
    if (inputFile == None):
        logging.fatal('Failed to open file ' + filename)
        exit(-1)
    
    logging.debug('Input CSV file opened.')
    
    connection = uniDWUtils.getConnection(config)
    logging.debug('Got db connection')

    c = insertEntries(connection, inputFile)
    logging.info('Timesheet inserts finished.  Inserted ' + str(c) + ' rows.');
    
except Exception as ex:
    logging.fatal('Failed in main timesheet importer with exception: ' + str(ex))

logging.debug('Cleaning up.')
if(connection != None): connection.close()
if(inputFile != None): inputFile.close()
logging.info('Timesheet importer done.')
