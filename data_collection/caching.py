from corona_sql import Session, Datapoint, Location
from sqlalchemy import or_, between, func
from datetime import date, datetime

import recounting

class DatapointCache(dict):
    def __init__(self, datapoints, session):
        for datapoint in datapoints:
            self.add(datapoint)

        self.session = session
        self.seen = set()
        self.was_updated = False
        self.potential_changes = set()
    
    def add(self, datapoint: Datapoint):
        self[datapoint.t] = datapoint

    def recount_changes(self):
        recounting.recount(self.potential_changes, cache=self)

    # "datas" is wrong but it's clear
    def update_all(self, datapoint_datas):
        for datapoint_data in datapoint_datas:
            self.update_data(datapoint_data)

    def update_data(self, datapoint_data, requireIncreasing=False):
        """Updates the data

        Arguments:
            datapoint_data {dict} -- contains the attributes

        Returns:
            tuple -- the new datapoint, and whether it was updated or not
        """
        def iso(d):
            if type(d) == date:
                return d.isoformat()
            else:
                return d

        t = datapoint_data['country'], datapoint_data['province'], datapoint_data['county'], iso(datapoint_data['entry_date'])
        
        if t in self.seen:
            return self[t], False
        else:
            self.seen.add(t)

        if t in self:
            if self[t].update(datapoint_data, requireIncreasing=requireIncreasing):
                self.potential_changes.update(self[t].parents())
                self.was_updated = True
        else:
            datapoint = Datapoint(datapoint_data)
            self.session.add(datapoint)
            self[t] = datapoint
            
            self.potential_changes.update(datapoint.parents())
            self.was_updated = True

    @staticmethod
    def create(rows, session):
        countries = {''}
        provinces = {''}

        max_entry_date = min_entry_date = rows[0]['entry_date']

        for row in rows:
            countries.add(row['country'])
            provinces.add(row['province'])

            row_date = row['entry_date']
            if row_date < min_entry_date:
                min_entry_date = row_date
            if row_date > max_entry_date:
                max_entry_date = row_date

        datapoints = session.query(Datapoint).filter(Datapoint.entry_date.between(min_entry_date, max_entry_date))
        
        if len(countries) <= 2:
            datapoints = datapoints.filter(Datapoint.country.in_(countries))

        if len(provinces) <= 2:
            datapoints = datapoints.filter(Datapoint.province.in_(provinces))

        return DatapointCache(datapoints, session)

class LocationCache(dict):
    def __init__(self, locations, session):
        for location in locations:
            self.add(location)
        
        self.session = session

    def add(self, location):
        self[location.location_tuple()] = location

    def update_data(self, new_data):
        country = new_data['country'] if 'country' in new_data else ''
        province = new_data['province'] if 'province' in new_data else ''
        county = new_data['county'] if 'county' in new_data else ''
        location_tuple = (country, province, county)

        if location_tuple in self:
            self[location_tuple].update(new_data)
        else:
            location = self[location_tuple] = Location(country=country, province=province, county=county)
            session.add(location)
            location.update(new_data)

    @staticmethod
    def create(rows, session):
        countries = {''}
        provinces = {''}

        for row in rows:
            countries.add(row['country'])
            provinces.add(row['province'])

        locations = session.query(Location)
        
        if len(countries) <= 2:
            locations = locations.filter(Location.country.in_(countries))

        if len(provinces) <= 2:
            locations = locations.filter(Location.province.in_(provinces))

        return LocationCache(locations, session)
