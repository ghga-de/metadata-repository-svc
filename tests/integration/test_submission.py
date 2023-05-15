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

from ..fixtures.mongodb import (  # noqa: F401
    BASE_DIR,
    MongoAppFixture,
    mongo_app_fixture3,
)


def test_create_submission(mongo_app_fixture3: MongoAppFixture):  # noqa: F811
    """Test creation of a Submission"""
    client = mongo_app_fixture3.app_client

    file_path = BASE_DIR / "test_data" / "submission_example" / "submission.json"
    with open(file_path, "r", encoding="utf8") as file:
        submission_json = json.load(file)

    response = client.post("/submissions", json=submission_json)
    submission_entity = response.json()
    # with open("test_submission.json", "w", encoding="utf-8") as sub:
    #    json.dump(submission_entity, sub, ensure_ascii=False, indent=4)
    assert "id" in submission_entity
    assert (
        submission_entity["has_study"]["has_project"]
        == submission_entity["has_project"]["id"]
    )

    assert (
        submission_entity["has_experiment"][0]["has_file"][0]
        == submission_entity["has_file"][0]["id"]
    )

    assert (
        submission_entity["has_experiment"][0]["has_protocol"][0]
        == submission_entity["has_protocol"][0]["id"]
    )

    assert "library_name" in submission_entity["has_protocol"][0]

    response = client.get(f"/submissions/{submission_entity['id']}?embedded=false")
    full_submission_entity = response.json()
    assert "submission_status" in full_submission_entity
    assert full_submission_entity["submission_status"] == "in_progress"

    submission_patch = {"submission_status": "completed"}
    response = client.patch(
        f"/submissions/{submission_entity['id']}", json=submission_patch
    )
    patched_submission = response.json()
    assert (
        patched_submission["submission_status"] == submission_patch["submission_status"]
    )
    assert patched_submission["creation_date"] == submission_entity["creation_date"]
    assert patched_submission["creation_date"] != patched_submission["update_date"]

    file_path = BASE_DIR / "test_data" / "submission_example" / "submission_update.json"
    with open(file_path, "r", encoding="utf8") as file:
        submission_update = json.load(file)

    response = client.put(
        f"/submissions/{submission_entity['id']}", json=submission_update
    )
    updated_submission = response.json()
    assert (
        updated_submission["has_project"]["title"]
        == submission_update["has_project"]["title"]
    )
    assert updated_submission["creation_date"] == submission_entity["creation_date"]
    assert updated_submission["creation_date"] != updated_submission["update_date"]
    assert updated_submission["update_date"] != patched_submission["update_date"]
