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


accuweather_weather_code_lookup = {1: 'Sunny',
                                   2: 'Mostly Sunny',
                                   3: 'Partly Sunny',
                                   4: 'Intermittent Clouds',
                                   5: 'Hazy Sunshine',
                                   6: 'Mostly Cloudy',
                                   7: 'Cloudy',
                                   8: 'Dreary (Overcast)',
                                   11: 'Fog',
                                   12: 'Showers',
                                   13: 'Mostly Cloudy w/ Showers',
                                   14: 'Partly Sunny w/ Showers',
                                   15: 'T-Storms',
                                   16: 'Mostly Cloudy w/ T-Storms',
                                   17: 'Partly Sunny w/ T-Storms',
                                   18: 'Rain',
                                   19: 'Flurries',
                                   20: 'Mostly Cloudy w/ Flurries',
                                   21: 'Partly Sunny w/ Flurries',
                                   22: 'Snow',
                                   23: 'Mostly Cloudy w/ Snow',
                                   24: 'Ice',
                                   25: 'Sleet',
                                   26: 'Freezing Rain',
                                   29: 'Rain and Snow',
                                   30: 'Hot',
                                   31: 'Cold',
                                   32: 'Windy',
                                   33: 'Clear',
                                   34: 'Mostly Clear',
                                   35: 'Partly Cloudy',
                                   36: 'Intermittent Clouds',
                                   37: 'Hazy Moonlight',
                                   38: 'Mostly Cloudy',
                                   39: 'Partly Cloudy w/ Showers',
                                   40: 'Mostly Cloudy w/ Showers',
                                   41: 'Partly Cloudy w/ T-Storms',
                                   42: 'Mostly Cloudy w/ T-Storms',
                                   43: 'Mostly Cloudy w/ Flurries',
                                   44: 'Mostly Cloudy w/ Snow'}

tomorrow_io_weather_code_lookup = {
    0: 'Unknown',
    1000: 'Clear',
    1001: 'Cloudy',
    1100: 'Mostly Clear',
    1101: 'Partly Cloudy',
    1102: 'Mostly Cloudy',
    2000: 'Fog',
    2100: 'Light Fog',
    3000: 'Light Wind',
    3001: 'Wind',
    3002: 'Strong Wind',
    4000: 'Drizzle',
    4001: 'Rain',
    4200: 'Light Rain',
    4201: 'Heavy Rain',
    5000: 'Snow',
    5001: 'Flurries',
    5100: 'Light Snow',
    5101: 'Heavy Snow',
    6000: 'Freezing Drizzle',
    6001: 'Freezing Rain',
    6200: 'Light Freezing Rain',
    6201: 'Heavy Freezing Rain',
    7000: 'Ice Pellets',
    7101: 'Heavy Ice Pellets',
    7102: 'Light Ice Pellets',
    8000: 'Thunderstorm',
}

weatherbit_wind_direction_lookup = {'north':  'N',
                                    'north-northeast':  'NNE',
                                    'northeast':  'NE',
                                    'east-northeast':  'ENE',
                                    'east':  'E',
                                    'east-southeast':  'ESE',
                                    'southeast':  'SE',
                                    'south-southeast':  'SSE',
                                    'south':  'S',
                                    'south-southwest':  'SSW',
                                    'southwest':  'SW',
                                    'west-southwest':  'WSW',
                                    'west':  'W',
                                    'west-northwest': 'WNW',
                                    'northwest': 'NW',
                                    'north-northwest':  'NNW'
                                    }

weatherbit_weather_code_lookup = {
    '200':	'Thunderstorm with light rain',
    '201':	'Thunderstorm with rain',
    '202':	'Thunderstorm with heavy rain',
    '230':	'Thunderstorm with light drizzle',
    '231':	'Thunderstorm with drizzle',
    '232':	'Thunderstorm with heavy drizzle',
    '233':	'Thunderstorm with Hail',
    '300':	'Light Drizzle',
    '301':	'Drizzle',
    '302':	'Heavy Drizzle',
    '500':	'Light Rain',
    '501':	'Moderate Rain',
    '502':	'Heavy Rain',
    '511':	'Freezing rain',
    '520':	'Light shower rain',
    '521':	'Shower rain',
    '522':	'Heavy shower rain',
    '600':	'Light snow',
    '601':	'Snow',
    '602':	'Heavy Snow',
    '610':	'Mix snow/rain',
    '611':	'Sleet',
    '612':	'Heavy sleet',
    '621':	'Snow shower',
    '622':	'Heavy snow shower',
    '623':	'Flurries',
    '700':	'Mist',
    '711':	'Smoke',
    '721':	'Haze',
    '731':	'Sand/dust',
    '741':	'Fog',
    '751':	'Freezing Fog',
    '800':	'Clear sky',
    '801':	'Few clouds',
    '802':	'Scattered clouds',
    '803':	'Broken clouds',
    '804':	'Overcast clouds',
    '900':	'Unknown Precipitation',
}
