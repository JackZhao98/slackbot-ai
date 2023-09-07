from api_manager import ApiManager
import os
import json


class AirmartDataCollector:
    def __init__(self, is_dev=False):
        self.is_dev = is_dev
        self.api_manager = ApiManager()

    def root_api_url(self):
        if self.is_dev:
            return "https://dev-ts-api.goairmart.com"
        else:
            return "https://ts-api.goairmart.com"

    def api_url(self, path):
        return self.root_api_url() + path

    def get_store_data(self, store_id):
        request_url = self.api_url("/v1/page/group/" + str(store_id))
        response = self.api_manager.get(request_url)
        return response.json()
