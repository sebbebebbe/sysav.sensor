"""
Sensor component for Sysav waste schedule integration
Original Author:  Sebastian Johansson
Current Version:  1.2

Description:
  Provides sensors for Sysav waste collecting schedule

Example config:
Configuration.yaml
  sensor:
    - platform: sysav
      streetname: Trädgårdsvägen               (required)
      streetnumber: 2                          (required)
      city: Bjärred                            (required)
      resources:
       - "Kärl 1"
       - "Kärl 2"
       - "Trädgårdsavfall"
"""

import logging
import json
from datetime import datetime
from datetime import timedelta
import voluptuous as vol
import urllib.request
import urllib.error

import sys
if sys.version_info.major > 2:  # Python 3 or later
    from urllib.parse import quote
else:  # Python 2
    from urllib import quote

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_RESOURCES
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=1)

CONF_STREET_NAME = "streetname"
CONF_STREET_NUMBER = "streetnumber"
CONF_CITY = "city"

SENSOR_PREFIX = "Sysav "
ATTR_LAST_UPDATE = "Last update"

SENSOR_TYPES = {
    "Kärl 1": ["Kärl 1", "", "mdi:delete"],
    "Kärl 2": ["Kärl 2", "", "mdi:delete"],
    "Matavfall": ["Matavfall", "", "mdi:delete"],
    "Restavfall": ["Restavfall", "", "mdi:delete"],
    "Trädgårdsavfall": ["Trädgårdsavfall", "", "mdi:delete"],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
        vol.Required(CONF_STREET_NAME, default=""): cv.string,
        vol.Required(CONF_STREET_NUMBER, default="1"): cv.string,
        vol.Required(CONF_CITY, default=""): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setup Sysav pickup times retriever")
    
    street_name = config.get(CONF_STREET_NAME)
    street_number = config.get(CONF_STREET_NUMBER)
    city = config.get(CONF_CITY)
    
    _LOGGER.debug("Sysav street_name: " + street_name)
    _LOGGER.debug("Sysav street_number: " + street_number)
    _LOGGER.debug("Sysav city: " + city)  

    try:
        data = SysavData(street_name, street_number, city)
    except urllib.error.HTTPError as error:
        _LOGGER.error(error.reason)
        return False

    entities = []
   
    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()
        _LOGGER.debug(sensor_type)
        _LOGGER.debug(resource)
        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [sensor_type.title(), "", "mdi:delete"]

        entities.append(SysavSensor(data, sensor_type))

    add_entities(entities)


class SysavData(object):
    def __init__(self, street_name, street_number, city):
        self.data = []
        self.street_name = street_name
        self.street_number = street_number
        self.city = city
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            suffix_url = self.street_name + " " + self.street_number + ", " + self.city
            suffix_url = urllib.parse.quote(suffix_url)
            url = "https://www.sysav.se/api/my-pages/PickupSchedule/ScheduleForAddress?address=" + suffix_url           
            req = urllib.request.Request(url=url)
            req.add_header('Accept','application/json, text/javascript, */*; q=0.01')
            f = urllib.request.urlopen(req)
            jsonData = json.load(f) 
            waste_array = []          
            for container in jsonData:
                waste_array.append(container) 
            _LOGGER.debug(waste_array)
            self.data = waste_array
        except urllib.error.URLError as exc:
            _LOGGER.error("Error occurred while fetching data: %r", exc.reason)
            self.data = None
            return False


class SysavSensor(Entity):
    def __init__(self, data, sensor_type):
        self.data = data
        self.type = SENSOR_TYPES[sensor_type][0]
        self._name = SENSOR_TYPES[sensor_type][0]
        self._unit = SENSOR_TYPES[sensor_type][1]
        self._icon = SENSOR_TYPES[sensor_type][2]
        self._date_format = "%d-%m-%Y"
        self._hidden = False
        self._state = None
        self._last_update = None

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return {ATTR_LAST_UPDATE: self._last_update}

    @property
    def unit_of_measurement(self):
        return self._unit

    def update(self):
        self.data.update()
        waste_data = self.data.data
        try:
            if waste_data:
                for container in waste_data:
                    if container.get('WasteType') == self.type:
                        self._state = container.get('NextPickupDate')
                        self._last_update = datetime.today()
        except ValueError:
            self._state = None
            self._hidden = True
