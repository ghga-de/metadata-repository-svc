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

"""
Submission through submission API
"""

import json

import requests
import typer


def ega_accession(field: str, sub_dict: dict) -> bool:
    """Check ega condition"""
    try:
        if sub_dict[field].startswith("EGA") and len(sub_dict[field]) == 15:
            return True
        return False
    except TypeError:
        return False


def ega_accession_update(field: str, sub_dict: dict) -> dict:
    """Update alias as ega acession"""
    if ega_accession(field, sub_dict):
        sub_dict.update({"ega_accession": sub_dict[field]})
    return sub_dict


def submission():
    """
    submit transpiled json to create datasets
    """
    file_path = "submission.json"  # This file has to be added to the scripts folder
    with open(file_path, "r", encoding="utf8") as file:
        submission_json = json.load(file)
    for item in submission_json:
        if item == "has_study":
            ega_accession_update("alias", submission_json[item])
        if item in [
            "has_dataset",
            "has_experiment",
            "has_publication",
            "has_data_access_committee",
            "has_data_access_policy",
            "has_member",
            "has_protocol",
            "has_file",
            "has_individual",
        ]:
            for key in submission_json[item]:
                ega_accession_update("alias", key)
        if item == "has_project":
            ega_accession_update("alias", submission_json[item])
        if item == "has_sample":
            for key in submission_json[item]:
                ega_accession_update("name", key)

    response = requests.post("http://localhost:8080/submissions", json=submission_json)
    print(response.status_code)


if __name__ == "__main__":
    typer.run(submission)
