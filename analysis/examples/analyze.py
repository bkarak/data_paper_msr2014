import pymongo


MONGO_HOST   = '83.212.106.194'
MONGO_DB     = 'findbugs'
MONGO_COL    = 'findbugs'
MONGO_UNAME  = 'findbugs'
MONGO_PASSWD = 'findbags'


def get_mongo_db():
    """
    Gets a connection to MongoDB
    """
    conn = pymongo.Connection(host=MONGO_HOST, max_pool_size=10, network_timeout=1)
    mongo_db = conn[MONGO_DB]
    mongo_db.authenticate(MONGO_UNAME, MONGO_PASSWD)
    
    return mongo_db

def record_exists(col_obj, group_id, artifact_id):
    try:
        q = {'JarMetadata.group_id' : group_id,
             'JarMetadata.artifact_id' : artifact_id}

        for c in col_obj.find(q, timeout=False):
            print c['JarMetadata']['version']
    except pymongo.errors.AutoReconnect, ae:
        print 'Mongo Connection is Down. Reconnecting! (record_exists, %s)' % (ae,)
        return record_exists(col_obj, group_id, artifact_id)
        
def count_security_category_records(col_obj, skip=0):
    counter = skip
    try:     
        q = {'BugCollection.BugInstance.category':'SECURITY'}
        
        for c in col_obj.find(q, timeout = False, skip=skip):
            for bi in c['BugCollection']['BugInstance']:
                if bi['category'] == 'SECURITY':                    
                    counter += 1
                    print counter
            
        print counter
    except pymongo.errors.AutoReconnect, ae:
        print 'Mongo Connection is Down. Reconnecting! (record_exists, %s)' % (ae,)
        count_security_category_records(col_obj, skip=counter)
                    

def main():
    mongo_db = get_mongo_db()
    col = mongo_db[MONGO_COL]
    count_security_category_records(col)
    #record_exists(col, 'org.apache.geronimo.modules', 'geronimo-j2ee-builder')
    
    

if __name__ == "__main__":
    main()
