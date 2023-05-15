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
"""Test the creation of submission via the API"""

import json

from ..fixtures.mongodb import BASE_DIR, mongo_app_fixture3  # noqa: F401


def test_retrieve_dataset_embedded(mongo_app_fixture3):  # noqa: F811
    """Test reading the embedded dataset"""
    client = mongo_app_fixture3.app_client

    file_path = BASE_DIR / "test_data" / "submission_example" / "submission.json"
    with open(file_path, "r", encoding="utf8") as file:
        submission_json = json.load(file)

    response = client.post("/submissions", json=submission_json)
    submission_entity = response.json()
    dataset_id = submission_entity["has_dataset"][0]["id"]

    response = client.get(f"/datasets/{dataset_id}?embedded=false")
    dataset_entity = response.json()

    experiment_entity = dataset_entity["has_experiment"][0]
    assert isinstance(experiment_entity, str)
    sample_entity = dataset_entity["has_sample"][0]
    assert isinstance(sample_entity, str)
    file_entity = dataset_entity["has_file"][0]
    assert isinstance(file_entity, str)

    response = client.get(f"/datasets/{dataset_id}?embedded=true")
    dataset_entity = response.json()

    experiment_entity = dataset_entity["has_experiment"][0]
    assert isinstance(experiment_entity, dict)
    sample_entity = dataset_entity["has_sample"][0]
    assert isinstance(sample_entity, dict)
    file_entity = dataset_entity["has_file"][0]
    assert isinstance(file_entity, dict)

    protocol_entity = dataset_entity["has_experiment"][0]["has_protocol"][0]
    assert len(protocol_entity.keys()) > 1
    sample_entity = dataset_entity["has_experiment"][0]["has_sample"][0]
    assert len(sample_entity.keys()) > 1
    file_entity = dataset_entity["has_experiment"][0]["has_file"][0]
    assert len(file_entity.keys()) > 1
