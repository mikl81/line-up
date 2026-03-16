# This file contains the possible request and response types for the authentication microservice
import json
from enum import IntEnum
from typing import Any


class RequestType(IntEnum):
    """ Possible request types """
    ADD_CREDENTIAL = 0
    VERIFY_CREDENTIAL = 1
    EDIT_CREDENTIAL = 2
    VERIFY_TOKEN = 3


class ResultType(IntEnum):
    """ Possible result/response types from a request """
    ADD_SUCCESS = 0
    ADD_FAIL_EXISTS = 1
    VERIFY_SUCCESS = 2
    VERIFY_FAIL_MISMATCH = 3
    VERIFY_FAIL_NOTFOUND = 4
    EDIT_SUCCESS = 5
    EDIT_FAIL_MISMATCH = 6
    EDIT_FAIL_NOTFOUND = 7
    BAD_REQUEST = 8  # When the request doesn't have the necessary/right data


def prep_request(req_type: RequestType, name: str, current_secret: str, new_secret: str = None):
    """ Given a request type and the secret(s) to send, creates a dict properly formatted for the service """
    if req_type == RequestType.EDIT_CREDENTIAL:
        req_data = {'name': name, 'current_secret': current_secret, 'new_secret': new_secret}
    else:
        req_data = {'name': name, 'secret': current_secret}

    return {"req_type": req_type, "req_data": req_data}


class RequestResult:
    """ Contains the ResultType and the data of the result """
    result_type: ResultType
    result_data: Any
    def __init__(self, _result_type: ResultType, _result_data: str):
        self.result_type = _result_type
        self.result_data = _result_data

    def toDict(self):
        new_dict = {
            "result_type": self.result_type,
            "result_data": self.result_data
        }
        return new_dict
