#
# facility to look up ids from the task_dim table to support inserting rows into fact tables referencing time_dim
#

import psycopg2
import logging
from pylru import lrucache

class TaskDimCache:
    """ simple cache of time dimension rows.  Uses an LRU since the full set
        of task dimension entries is large and for any given timesheet importer run, the
        timesheet tasks will likely be frequently re-used.
    """

    def __init__(self):
        self.maxLen = 1500  # WAG that 150 employees has 
        self.myCache = lrucache(self.maxLen)    # probably really only need about a month at a time


    # Get a time_dim ID given a date
    # if not in the cache, load it from the time_dim table
    # returns None if something goes wrong or can't find the given date entry.  maybe mod to just insert if not found?
    def get(self, dbConn, date):

        val = self.myCache(date)
        logging.debug('TimeDimCache - checked for ' + date + ' got ' + str(val))
        if val==None:
           # not in the cache, load it from table
           logging.debug('TimeDimCache miss:  loading ' + date)
           cnt = self.load(dbConn, date)
           logging.debug('TimeDimCache miss: loaded ' + str(cnt))
           val = self.myCache(date)
        return val

    
    # load a row into the cache
    # return the number of rows loaded, 0 indicates an error (or empty table)
    # date is 
    def load(self, dbConn, date):
        
        cur = None
        try:
            cur = dbConn.cursor()
        except Exception as ex:
            logging.warn('Failed to get cursor: ' + str(ex))
            return 0

        try:
            cur.execute('select person_id, first_name, last_name from unicon_dw.person_dim')
        except Exception as ex:
            logging.warn('Failed to execute select: ' + str(ex))
            return 0

        try:
            cnt = 0
            rows = cur.fetchone()  
            for r in rows:
                self.myCache[date] = r[0]  # date is the key, the time_dim_id is the value
                cnt += 1
                logging.debug('timeDimCache - Key: ' + str(date) + ' Value: ' + str(r[0]))
        except Exception as ex:
            logging.warn('Failed loading data: ' + str(ex))
        finally:
            cur.close()
            return(cnt)

           
            

        
