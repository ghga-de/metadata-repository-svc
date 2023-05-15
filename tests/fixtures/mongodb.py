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

"""Fixture that setup and tears down a MongoDB database together with a correspondingly
configured app client."""

import json
import os
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from testcontainers.mongodb import MongoDbContainer

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.api.main import app
from metadata_repository_service.config import Config

from . import BASE_DIR


@dataclass
class MongoAppFixture:
    app_client: TestClient
    config: Config


@pytest.fixture(scope="function")
def mongo_app_fixture1():
    """
    Setup a MongoDB database with basic metadata examples.
    """

    json_files = [
        ("datasets.json", "Dataset"),
        ("studies.json", "Study"),
        ("experiments.json", "Experiment"),
        ("biospecimens.json", "Biospecimen"),
        ("samples.json", "Sample"),
    ]

    with MongoDbContainer() as mongodb:
        connection_url = mongodb.get_connection_url()
        db_client = mongodb.get_connection_client()
        config = Config(db_url=connection_url, db_name="test")

        for filename, collection_name in json_files:
            file_path = BASE_DIR / "test_data" / "basic_example" / filename
            with open(file_path, "r", encoding="utf8") as file:
                file_content = json.load(file)
                objects = file_content[os.path.splitext(filename)[0]]
                db_client[config.db_name][collection_name].insert_many(objects)

        app.dependency_overrides[get_config] = lambda: config
        app_client = TestClient(app)

        yield MongoAppFixture(app_client=app_client, config=config)


@pytest.fixture(scope="function")
def mongo_app_fixture2():
    """
    Setup a MongoDB database with metadata for testing of creation of a Dataset.
    """

    json_files = [
        ("biospecimens.json", "Biospecimen"),
        ("experiments.json", "Experiment"),
        ("files.json", "File"),
        ("individuals.json", "Individual"),
        ("projects.json", "Project"),
        ("samples.json", "Sample"),
        ("studies.json", "Study"),
        # ("technologies.json", "Technology"),
    ]

    with MongoDbContainer() as mongodb:
        connection_url = mongodb.get_connection_url()
        db_client = mongodb.get_connection_client()
        config = Config(db_url=connection_url, db_name="test")

        for filename, collection_name in json_files:
            file_path = BASE_DIR / "test_data" / "create_dataset_example" / filename
            with open(file_path, "r", encoding="utf8") as file:
                file_content = json.load(file)
                objects = file_content[os.path.splitext(filename)[0]]
                db_client[config.db_name][collection_name].insert_many(objects)

        app.dependency_overrides[get_config] = lambda: config
        app_client = TestClient(app)

        yield MongoAppFixture(app_client=app_client, config=config)


@pytest.fixture
def mongo_app_fixture3():
    """
    Setup an empty MongoDB database.
    """

    with MongoDbContainer() as mongodb:
        connection_url = mongodb.get_connection_url()
        config = Config(db_url=connection_url, db_name="test")

        app.dependency_overrides[get_config] = lambda: config
        app_client = TestClient(app)

        yield MongoAppFixture(app_client=app_client, config=config)
