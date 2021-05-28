import tornado.ioloop
import tornado.web
import tornado.gen
import json
from dotenv import load_dotenv
from weather_clients.factory import Factory


# Load env variables
load_dotenv()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # print('self', self.get_query_argument('a'))
        self.write("Hello, world")


class SingleWeatherHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        weather_client = Factory().instantiate_member('WeatherbitIoClient')
        weather_client2 = Factory().instantiate_member('AccuWeatherClient')
        weather_client3 = Factory().instantiate_member('OpenWeatherClient')
        weather_client4 = Factory().instantiate_member('MetOfficeClient')
        data = yield [weather_client.get_forecast_lat_lon(lat=50.73862, lon=-2.90325),
                      weather_client2.get_forecast_lat_lon(
                          lat=50.73862, lon=-2.90325),
                      weather_client3.get_forecast_lat_lon(
                          lat=50.73862, lon=-2.90325),
                      weather_client4.get_forecast_lat_lon(lat=50.73862, lon=-2.90325)]

        self.write(json.dumps(data, default=str))


class WeatherHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        factory = Factory()
        weather_clients = factory.instantiate_all_members()
        all_forecasts = yield {cls.__class__.__name__: cls.get_forecast_lat_lon(
            lat=50.73862, lon=-2.90325) for cls in weather_clients}
        self.write(json.dumps(all_forecasts, indent=4,
                   sort_keys=True, default=str))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/single_weather", SingleWeatherHandler),
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
