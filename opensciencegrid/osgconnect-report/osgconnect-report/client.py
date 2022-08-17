#!/usr/bin/env python3
import os
import requests
import logging
import sys
import json
from pathlib import Path
from typing import List, Dict

# https://github.com/maniaclab/ci-connect-api/blob/master/resources/api_specification/api.raml
class UserApiClient:
    """Simple client class for making GET requests to OSG Connect Database"""

    def __init__(self, token_file_path: Path):
        """Constructor

        :param token_file_path: path to file containing API token
        :type token_file_path: str
        """
        self.log = logging.getLogger("Client")
        self.url_prefix = "https://api.ci-connect.net:18080/v1alpha1"
        try:
            with token_file_path.open("r") as f:
                self._token = f.read().strip()
        except FileNotFoundError:
            self.log.exception("Unable to find token file.")
            sys.exit(1)

    def _get(self, route: str) -> Dict:
        """Internal use GET method

        :param route: route to GET
        :type route: str
        :return: dict representation of response
        :rtype: Dict
        :raises requests.exceptions.HTTPError: encountered 4XX client error or 5XX server error response
        """
        resp = requests.get("{}{}?token={}".format(
                self.url_prefix, route, self._token
            ))

        # ensure status code 200
        resp.raise_for_status()

        return resp.json()

    ### User Level Requests ####################################################
    def get_users(self) -> List[Dict]:
        """Get all users

        :return: each users with detailed information (not including group memberships)
        :rtype: List[Dict]
        """
        resp = self._get("/users")
        return resp["items"]
    
    def get_user(self, uid: str) -> Dict:
        """Get detailed information about a specific user

        :param uid: user's id such as "jimhalpert"
        :type uid: str
        :return: detailed user information
        :rtype: Dict
        """
        resp = self._get("/users/{uid}".format(uid=uid))
        return resp
    
    ### Group Level Requests ###################################################
    def get_group_list(self) -> List[str]:
        """Get a list of all group names

        :return: all group names
        :rtype: List[str]
        """
        resp = self._get("/groups")  
        return [group["name"] for group in resp["groups"]]

    def get_group(self, group_name: str) -> Dict:
        """Get a specific group

        :param group_name: name of the group such as root.osg.NameOfGroup
        :type group_name: str
        :return: group information not including members
        :rtype: Dict
        """
        resp = self._get("/groups/{g_name}".format(g_name=group_name))
        return resp

    def get_group_members(self, group_name: str) -> List[Dict]:
        """Get all members in the specified group

        :param group_name: name of the group such as root.osg.NameOfGroup
        :type group_name: str
        :return: each member in the given group
        :rtype: List[Dict]
        """
        resp = self._get("/groups/{g_name}/members".format(g_name=group_name))
        return [member for member in resp["memberships"]]

    



