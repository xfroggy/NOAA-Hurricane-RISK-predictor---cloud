from pysnmp import hlapi
import pandas as pd
from pymongo import MongoClient

def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    return fetch(handler, 1)[0]

def get_bulk(target, oids, credentials, count, start_from=0, port=161,
             engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.bulkCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        start_from, count,
        *construct_object_types(oids)
    )
    return fetch(handler, count)   

def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
    return object_types    

def fetch(handler, count):
    result = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                result.append(items)
            else:
                raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
        except StopIteration:
            break
    return result

def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value        



# get data from OIDs and add it to a dataframe
# assume 1000 readings happening every 3 minutes, get and add to collection.
# data = pd.???

# after reading, baseline checks - are values within normal range? 
# if not send error or report 

# Connect to MongoDB
client =  MongoClient("")
db = client['<<DATABASENAME>>']
collection = db['<<COLLECTIONNAME>>']
data.reset_index(inplace=True)
data_dict = data.to_dict("records")

# Insert collection
collection.insert_many(data_dict)

