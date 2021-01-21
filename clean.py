import pandas as pd
import numpy as np


def clean(data_url):
  
    hurricane_dt = pd.read_csv(
        data_url,
        names=['date', 'time', 'record_id', 'status', 'latitude', 'longitude', 'max_wind', 'min_pressure', 'ne34ktr', 'se34ktr', 'sw34ktr', 'nw34ktr', 'ne50ktr', 'se50ktr', 'sw50ktr', 'nw50ktr', 'ne64ktr', 'se64ktr', 'sw64ktr', 'nw64ktr'], skipinitialspace=True
    )


    # boolean expr to mask and isolate the identifier rows
    mask = hurricane_dt.date.str[:2] == "AL"
    header_rows = hurricane_dt[mask]

    # create new 'identifier' column with data from the isolated identifier rows
    hurricane_dt['identifier'] = header_rows['date']

    # create new 'name' column with data from the isolated identifier rows
    hurricane_dt['name'] = header_rows['time']

    # create new 'num_pts' column with data from the isolated identifier rows
    hurricane_dt['num_pts'] = header_rows['record_id']

    # remove these newly created columns from end
    first_col = hurricane_dt.pop('identifier')
    second_col = hurricane_dt.pop('name')
    third_col = hurricane_dt.pop('num_pts')

    # insert newly created columns at beginning
    hurricane_dt.insert(0, 'identifier', first_col)
    hurricane_dt.insert(1, 'name', second_col)
    hurricane_dt.insert(2, 'num_pts', third_col)

    # forward fill the Nan cells so that each row has 'identifier', 'name', 'num_pts'
    hurricane_dt['identifier'] = hurricane_dt['identifier'].fillna(method='ffill')
    hurricane_dt['name'] = hurricane_dt['name'].fillna(method='ffill')
    hurricane_dt['num_pts'] = hurricane_dt['num_pts'].fillna(method='ffill')

    # remove the identifier rows
    hurricane_dt.drop(
        hurricane_dt[hurricane_dt['status'].isnull()].index, inplace=True)

    # replace UNNAMMED and -999 with Nan
    hurricane_dt['name'] = hurricane_dt['name'].replace("UNNAMED", np.nan)
    hurricane_dt = hurricane_dt.replace(-999, np.nan)

    # convert date and time objects to datetime of type datetime and replace date/time columns
    hurricane_dt['datetime'] = pd.to_datetime(
        (hurricane_dt['date'])+(hurricane_dt['time']))
    date_time_col = hurricane_dt.pop('datetime')
    hurricane_dt.insert(3, 'datetime', date_time_col)
    hurricane_dt = hurricane_dt.drop(['date', 'time'], axis=1)

    # convert latitude to floats (with S values as negative)
    hurricane_dt['lat_direction'] = (
        hurricane_dt.latitude.str[-1:] == "N").astype(int)
    hurricane_dt['temp_latitude'] = (hurricane_dt.latitude.str[:-1]).astype(float)

    # convert longitude to floats (with W values as negative)
    hurricane_dt['long_direction'] = (
        hurricane_dt.longitude.str[-1:] == "E").astype(int)
    hurricane_dt['temp_longitude'] = (
        hurricane_dt.longitude.str[:-1]).astype(float)

    # create temporary -1  for S and W, 1 for N and E
    hurricane_dt[['long_direction', 'lat_direction']
                ] = hurricane_dt[['long_direction', 'lat_direction']].replace(0, -1)

    # update latitude and longitude columns with new values
    hurricane_dt['latitude'] = hurricane_dt['temp_latitude'] * \
        hurricane_dt['lat_direction']
    hurricane_dt['longitude'] = hurricane_dt['temp_longitude'] * \
        hurricane_dt['long_direction']

    # remove temp columns and convert final columns to correct type
    hurricane_dt = hurricane_dt.drop(
        ['temp_latitude', 'lat_direction', 'temp_longitude', 'long_direction'], axis=1)
    hurricane_dt['num_pts'] = hurricane_dt['num_pts'].astype(int)

    #hurricane_dt[['latitude', 'longitude']]
    return hurricane_dt
