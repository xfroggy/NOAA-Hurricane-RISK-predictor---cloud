from datetime import timedelta
import math
import numpy as np
import pandas as pd
import altair as alt
from altair import datum
from vega_datasets import data



class Prediction:
    
    # array that will store list of storms that hit location coordinates
    
    
    def __init__(self, full_storm_data, location, radius, impact):
        self.full_storm_data = full_storm_data
        self.location = location
        self.radius = radius
        self.impact = impact
        
        # array of hurricanes that have hit location, starts empty
        self.hurricane_history = []
        
        #filter for only storms that became hurricanes
        self.df_hu = self.full_storm_data[self.full_storm_data['status'] == 'HU']
        
        # df of all rows for unique storms that attained hurricane status
        self.total_hu = self.df_hu['identifier'].unique()
        
        # total number of hurricanes in df
        self.total_num_hu = len(self.total_hu)
        
        # total number of hurricanes that have hit location
        self.total_hits = self.get_hits()
        
        # Probability of Occurrence
        self.PoC = round((len(self.hurricane_history)/len(self.total_hu)),4)
        
        self.rank = self.rank_PoC()
        
        self.risk = self.PoC*self.impact
        
        self.map_of_storms = self.map_hu()
        
    
  
    def get_hits(self):
        #print(self.total_hu)
        # iterate through list of coordinates for each storm, checking to see if the paths cross location coordinates
        for storm in self.total_hu:
            
            current = self.full_storm_data[self.full_storm_data['identifier']== storm]
            initial_reading = current.head(1)
            
            
            # determine if storm started South of location coordinates
            starts_South = initial_reading['latitude'] < self.location.latitude
            if (starts_South.item() == True):
                coord_name = 'latitude'
                if self.nearest_coord(coord_name, current):
                    
                    #if there's a hit at latitude, no need to check longitude
                    continue
                
            # determine if storm started East of location coordinates
            starts_East = initial_reading['longitude'] < self.location.longitude
            if (starts_East.item() == True):
                coord_name = 'longitude'
           
        return len(self.hurricane_history)
        
    def nearest_coord(self, coord_name, current):
            # get 2 points closest to the location to form a line, 
            # then pass these readings to 'checkCollision' to see if line intersects 
            # wwith the radius around the location
    
            # get first location after crossing latitude or longitude (if it crosses)
            if coord_name == 'latitude':
                mask = current[coord_name] >= self.location.latitude
            else:
                mask = current[coord_name] >= self.location.longitude
                
            point_A = current[mask].head(1)
            # if it crosses, find previous location reading
            if not point_A.empty:
                point_B = current[
                    (current['datetime'] >= (point_A['datetime'].item() - timedelta(hours=6))) & (current['datetime'] < point_A['datetime'].item())
                    ]
                    
                # data is not always in 6 hour increments so if more than 1 reading in previous 6 hours, take the latest
                point_B = point_B.tail(1)  
              
                # check if line between point A and B crosses through circle of radius around location
                if self.checkCollision(point_A, point_B):
                    self.hurricane_history.append(point_A['identifier'].item())
                    return True
            else:
                return False

    def checkCollision(self, P, Q): 
            x1 = P['latitude'].item()
            y1 = P['longitude'].item()
            x2 = Q['latitude'].item()
            y2 = Q['longitude'].item()
            
            x=self.location.latitude
            y=self.location.longitude
        
            # formula for the perpendicular distance of the location (point) to the line
            dist = abs(((y1-y2)*x)+((x2-x1)*y) + (x1*y2) - (x2*y1)) / math.sqrt(((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1)))
        
            if (self.radius == dist) or (self.radius > dist): 
               # touches or intersects radius
                return True
            else: 
               # outside of radius 
                return False    
                
    def rank_PoC(self):
        
        highest_concentration = .0303 # at .50 radius
    
        #get CHC (Current Highest Concentration) at actual radius
        CHC = (highest_concentration*self.radius) / .5
    
        rank_interval = CHC /5
        if self.PoC >= CHC:
            return "High"
        elif (self.PoC) and (self.PoC >= (CHC-rank_interval)):
            return "Medium-High"
        elif (self.PoC <= (CHC-rank_interval)) and (self.PoC > (CHC-(rank_interval*2))):       
            return "Medium"
        elif (self.PoC <= (CHC-(rank_interval*2))) and (self.PoC > (CHC-(rank_interval*3))):   
            return "Medium-Low"
        else:
            return "Low"    

    def map_hu(self):
        hurricanes_full_set = self.full_storm_data[self.full_storm_data['identifier'].isin(self.hurricane_history)]
        world = data.world_110m.url
        the_map = alt.layer(
            # use the sphere of the Earth as the base layer
            alt.Chart({'sphere': True}).mark_geoshape(
                fill='#e6f3ff'
            ),
            # add a graticule for geographic reference lines
            alt.Chart({'graticule': True}).mark_geoshape(
                stroke='#ffffff', strokeWidth=1
            ),
            # and then the countries of the world
            alt.Chart(alt.topo_feature(world, 'countries')).mark_geoshape(
                fill='#2a1d0c', stroke='#706545', strokeWidth=0.5
            ),
            # plot paths of hurricanes that have hit location
            alt.Chart(hurricanes_full_set).mark_line(
                strokeWidth = 2,
                opacity = 0.5,
                ).encode(
                latitude = 'latitude:Q',
                longitude = 'longitude:Q',
                color = alt.Color('identifier:N', legend=None),
                tooltip = ['name:N', 'identifier:N', 'year(datetime)', 'latitude:Q', 'longitude:Q']    
            ),
           
        ).project(
            type='mercator', scale = 400, translate=[700,350]
        ).properties(width=600, height=400
        )

        return the_map.to_json()
