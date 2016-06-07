#
# facility to look up ids from the time_dim table to support inserting rows into fact tables referencing time_dim
#

import psycopg2
import logging
from pylru import lrucache

class TimeDimCache:
    """ simple cache of time dimension rows.  Uses an LRU since the full set
        of time dimension entries is large and for any given timesheet importer run, the
        timesheet dates will likely be frequently re-used.
    """

    def __init__(self):
        self.maxLen = 64
        self.myCache = lrucache(self.maxLen)    # 64 entries since generally importing a month at a time (ish), plus extra


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
            logging.debug('loading time dim for date: ' + date)
            cur.execute('select entry_date from unicon_dw.time_dim where entry_date = ' + str(date))
        except Exception as ex:
            logging.warn('Failed to execute select: ' + str(ex))
            return 0

        try:
            cnt = 0
            rows = cur.fetch()  
            for r in rows:
                self.myCache[date] = r[0]  # date is the key, the time_dim_id is the value
                cnt += 1
                logging.debug('timeDimCache - Key: ' + date + ' Value: ' + str(r[0]))
        except Exception as ex:
            logging.warn('Failed loading data: ' + str(ex))
        finally:
            cur.close()
            return(cnt)

           
            

        
