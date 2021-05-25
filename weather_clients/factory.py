from inspect import getmembers, isclass, isabstract
from weather_clients import weather_apis


class Factory:
    def __init__(self) -> None:
        self._members = self.load_members()

    def load_members(self):
        output = {}
        for name, cls in getmembers(weather_apis):
            if isclass(cls) and not isabstract(cls):
                output[name.lower()] = cls
        return output

    def instantiate_all_members(self):
        return [cls() for name, cls in self._members.items()]

    def instantiate_member(self, api_name: str):
        return self._members[api_name.lower()]()
