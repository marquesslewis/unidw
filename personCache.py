#
# facility to look up person ids from the person_dim table to support inserting rows into fact tables referencing employee
#

import psycopg2
import logging

class PersonCache:
    """simple cache of persons.  Assumes they all fit in memory"""

    def __init__(self):
        self.data = {}  #stupid dictionary with keys of first+last to get ID

    # load up the cache from the db table
    # return the number of rows loaded, 0 indicates an error (or empty table)
    def load(self, dbConn):
        
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
            rows = cur.fetchall()  # may eventually be a bad idea to load all at once
            for r in rows:
                self.data[r[2]+', '+r[1]] = r[0]  # concat first name, last name to form key, the person_id is the value
                cnt += 1
                logging.debug('PersonCache - Key: ' + r[2]+', '+r[1] + ' Value: ' + str(r[0]))
        except Exception as ex:
            logging.warn('Failed loading data: ' + str(ex))
        finally:
            cur.close()
            return(cnt)

    # retrieve id given first name and last name
    #
    def get(self, fn, ln):
        try:
            return self.data[ln+', '+fn]
        except KeyError:
            logging.info('PersonCache.get(): no entry for ' + fn+ln)
            return None
        

    # retrieve id given key
    #
    def get(self, nm):
        try:
            return self.data[nm]
        except KeyError:
            logging.info('PersonCache.get(): no entry for ' + nm)
            return None            
            

        
