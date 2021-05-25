import tornado.ioloop
import tornado.web
import json
from dotenv import load_dotenv
from weather_clients.factory import Factory


# Load env variables
load_dotenv()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # print('self', self.get_query_argument('a'))
        self.write("Hello, world")


class AccuWeatherHandler(tornado.web.RequestHandler):
    async def get(self):
        accuweather = Factory().instantiate_member('AccuWeatherClient')
        data = await accuweather.get_forecast_lat_lon(lat=50.73862, lon=-2.90325)
        self.write(json.dumps(data, default=str))


class WeatherHandler(tornado.web.RequestHandler):
    async def get(self):
        factory = Factory()
        weather_clients = factory.instantiate_all_members()
        all_forecasts = await {cls.__class__.__name__: cls.get_forecast_lat_lon(
            lat=50.73862, lon=-2.90325) for cls in weather_clients}
        self.write(json.dumps(all_forecasts, indent=4,
                   sort_keys=True, default=str))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/accuweather", AccuWeatherHandler),
        (r"/get_weather", WeatherHandler),
    ], debug=True, autoreload=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

# accuweather = AccuWeatherClient()
# print('accuweather get_forecast_lat_lon', accuweather.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('accuweather get_forecast_postcode',
#       accuweather.get_forecast_postcode('GB', 'b17 0hs'))
# print('accuweather get_forecast_city_country',
#       accuweather.get_forecast_city_country("Birmingham", "uk"))
