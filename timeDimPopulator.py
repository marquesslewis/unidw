"""
Script to populate the time_dim dimension table with dates, and respective attributes for time-based filtering and analysis


"""


import psycopg2
import string
import logging
import datetime
import uniDWUtils

gCommitBoundary = 200
gStartYear=2010
gEndYear=2020


#########################################################
# insert the time rows
#
def insertTimes(conn):
    
    global gCommitBoundary
    global gStartYear
    rowCount = 0
    
    try:
        cursor = conn.cursor()
    except Exception as ex:
        logging.error('failed to get cursor: ' + str(ex))
        return rowCount
    
    try:
        logging.debug('starting time generation')
        date = datetime.date(gStartYear, 1, 1)
        while date.year <= gEndYear:
            rowCount += 1
            
            #get the y, d, m, q
            yr = date.year
            day = date.day
            month = date.month
            quarter = ((month-1)/3)+1
            
            #construct insert stmt
            insertStmt = 'insert into unicon_dw.time_dim(entry_date, day_of_month, month, quarter, year) ' + \
                         "values ('%s', '%s', '%s', '%s', '%s')" % (str(date), day, month, quarter, yr)
            logging.debug(insertStmt)
            
            #do it
            cursor.execute(insertStmt)
            if(rowCount%gCommitBoundary == 0):
                conn.commit()
                logging.debug('Committed ' + str(gCommitBoundary))

            #bump the day
            date = date + datetime.timedelta(1)            
            
    except Exception as ex:
        logging.error('Failed inserting at row ' + str(rowCount) + ' ex: ' + str(ex))
        cursor.close()
        return rowCount

    conn.commit()
    cursor.close()
    
    return rowCount

#########################################################
# main script
#

connection=None

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

try:
    logging.info('Starting time dimension populator.')
    
    # read config file
    config = uniDWUtils.getConfig('config.cfg')    
    logging.debug('Config: ' + str(config))
    
    connection = uniDWUtils.getConnection(config)
    logging.debug('Got db connection')

    c = insertTimes(connection)
    logging.info('Inserts finished.  Inserted ' + str(c) + ' rows.');
    
except Exception as ex:
    logging.fatal('Failed in main time populator with exception: ' + str(ex))

logging.debug('Cleaning up.')
if(connection != None): connection.close()
logging.info('Time dimension populator done.')
