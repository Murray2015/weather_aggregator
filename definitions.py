no_data_value = 99999

weather_lookup_codes = {
    'NA':	'Not available',
    '0':	'Clear night',
    '1':	'Sunny day',
    '2':	'Partly cloudy (night)',
    '3':	'Partly cloudy (day)',
    '4':	'Not used',
    '5':	'Mist',
    '6':	'Fog',
    '7':	'Cloudy',
    '8':	'Overcast',
    '9':	'Light rain shower (night)',
    '10':	'Light rain shower (day)',
    '11':	'Drizzle',
    '12':	'Light rain',
    '13':	'Heavy rain shower (night)',
    '14':	'Heavy rain shower (day)',
    '15':	'Heavy rain',
    '16':	'Sleet shower (night)',
    '17':	'Sleet shower (day)',
    '18':	'Sleet',
    '19':	'Hail shower (night)',
    '20':	'Hail shower (day)',
    '21':	'Hail',
    '22':	'Light snow shower (night)',
    '23':	'Light snow shower (day)',
    '24':	'Light snow',
    '25':	'Heavy snow shower (night)',
    '26':	'Heavy snow shower (day)',
    '27':	'Heavy snow',
    '28':	'Thunder shower (night)',
    '29':	'Thunder shower (day)',
    '30':	'Thunder',
}
visibility_lookup_codes = {
    'UN': 	'Unknown',
    'VP': 	'Very poor - Less than 1 km',
    'PO': 	'Poor - Between 1-4 km',
    'MO': 	'Moderate - Between 4-10 km',
    'GO': 	'Good - Between 10-20 km',
    'VG': 	'Very good - Between 20-40 km',
    'EX': 	'Excellent - More than 40 km',
}
uv_lookup_codes = {
    '0':  	'Low exposure. No protection required. You can safely stay outside',
    '1':  	'Low exposure. No protection required. You can safely stay outside',
    '2':  	'Low exposure. No protection required. You can safely stay outside',
    '3':  	'Moderate exposure. Seek shade during midday hours, cover up and wear sunscreen',
    '4':  	'Moderate exposure. Seek shade during midday hours, cover up and wear sunscreen',
    '5':  	'Moderate exposure. Seek shade during midday hours, cover up and wear sunscreen',
    '6':  	'High exposure. Seek shade during midday hours, cover up and wear sunscreen',
    '7':  	'High exposure. Seek shade during midday hours, cover up and wear sunscreen',
    '8':  	'Very high. Avoid being outside during midday hours. Shirt, sunscreen and hat are essential',
    '9':  	'Very high. Avoid being outside during midday hours. Shirt, sunscreen and hat are essential',
    '10':  	'Very high. Avoid being outside during midday hours. Shirt, sunscreen and hat are essential',
    '11':  'Extreme. Avoid being outside during midday hours. Shirt, sunscreen and hat essential.',
}


def open_weather_visibility_lookup(visibility_metres: int) -> str:
    """ Returns a string of the visibility based on a the visibility in metres """
    if visibility_metres < 1000:
        return 'Very poor - Less than 1 km'
    elif visibility_metres < 4000:
        'Poor - Between 1-4 km'
    elif visibility_metres < 10000:
        return 'Moderate - Between 4-10 km'
    elif visibility_metres < 20000:
        return 'Good - Between 10-20 km'
    elif visibility_metres < 40000:
        return 'Very good - Between 20-40 km'
    elif visibility_metres < 100000:
        return 'Excellent - More than 40 km'
    else:
        return 'Unknown'


def open_weather_wind_direction_lookup(direction_deg: int) -> str:
    if 330 <= direction_deg <= 25:
        return 'N'
    elif 25 <= direction_deg <= 60:
        return 'NE'
    elif 60 <= direction_deg <= 120:
        return 'E'
    elif 120 <= direction_deg <= 160:
        return 'SE'
    elif 160 <= direction_deg <= 200:
        return 'S'
    elif 200 <= direction_deg <= 240:
        return 'SW'
    elif 240 <= direction_deg <= 280:
        return 'W'
    elif 280 <= direction_deg <= 330:
        return 'NW'
    else:
        return 'Unknown'
