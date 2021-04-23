from abc import ABC, abstractmethod


class Asset(ABC):
    "Interface for asset based classes"
    name: str
    asset_type: str

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, name: str):
        self.name = name

    @property
    def asset_type(self):
        return self.asset_type

    @asset_type.setter
    def asset_type(self, asset_type: str):
        self.asset_type = asset_type


class Portfolio:
    pass
