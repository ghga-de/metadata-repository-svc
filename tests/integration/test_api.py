# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test the api module"""

import pytest
from fastapi import status

from ..fixtures.mongodb import MongoAppFixture, mongo_app_fixture1  # noqa: F401


def test_index(mongo_app_fixture1: MongoAppFixture):  # noqa: F811
    """Test the index endpoint"""

    client = mongo_app_fixture1.app_client
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.text == '"Index of the Metadata Repository Service"'


@pytest.mark.parametrize(
    "route,entity_id,check_conditions",
    [
    ],
)
def test_get_entity_by_id(
    mongo_app_fixture1: MongoAppFixture,  # noqa: F811
    route,
    entity_id,
    check_conditions,
):
    client = mongo_app_fixture1.app_client

    response = client.get(f"/{route}/{entity_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data and data["id"] == entity_id
    for key, value in check_conditions.items():
        assert key in data and data[key] == value
