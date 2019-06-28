import json

import pytest

from simple_ecs_service_scheduler import app


@pytest.fixture()
def cwrules_event():
    """ Generates CloudWatch Event"""

    return {"rulename": "7amweekdays", "behavior": "scaledown"}

def test_lambda_handler(cwrules_event, mocker):

    ret = app.lambda_handler(cwrules_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "tbd"
    # assert "location" in data.dict_keys()
