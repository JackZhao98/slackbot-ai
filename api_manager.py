import requests
import json
import os
import time

# enum for the different types of API calls
# GET, POST, PUT, DELETE
from enum import Enum

HTTPMethod = Enum("HTTPMethod", ["GET", "POST", "PUT", "DELETE"])


class ApiManager:
    def __init__(self, lang="en", access_token=None, bearer_token=None):
        self.user_agent = "SlackBot V1.0"
        self.lang = lang
        self.access_token = access_token
        self.bearer_token = bearer_token

    def set_access_token(self, access_token):
        self.access_token = access_token

    def set_bearer_token(self, bearer_token):
        self.bearer_token = bearer_token

    def get_headers(self):
        headers = {
            "User-Agent": self.user_agent,
            "lang": self.lang,
            "Content-Type": "application/json",
        }
        if self.access_token:
            headers["access-token"] = self.access_token
        if self.bearer_token:
            headers["Authorization"] = "Bearer " + self.bearer_token

        return headers

    def get(self, url, data=None):
        return requests.get(url, headers=self.get_headers(), data=data)

    def operation(self, url, data=None):
        if self.method == HTTPMethod.GET:
            return self.get(url, data)
        elif self.method == HTTPMethod.POST:
            return self.post(url, data)
        elif self.method == HTTPMethod.PUT:
            return self.put(url, data)
        elif self.method == HTTPMethod.DELETE:
            return self.delete(url, data)
        else:
            raise Exception("Invalid HTTP Method")
