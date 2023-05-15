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
Convenience methods for retrieving Submission records
"""

import copy
from typing import Dict, List

from pymongo import ReturnDocument

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.creation_models import CreateSubmission
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import (
    delete_document,
    embed_references,
    get_timestamp,
    link_embedded,
    parse_document,
    store_document,
    update_document,
)
from metadata_repository_service.models import Submission
from metadata_repository_service.patch_models import SubmissionStatusPatch

COLLECTION_NAME = "Submission"


async def retrieve_submissions(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Submission object IDs from metadata store.

    Args:
        config: Runtime configuration

    Returns:
        A list of Submission object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    submissions = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in submissions]


async def get_submission(
    submission_id: str, embedded: bool = False, config: Config = CONFIG
) -> Submission:
    """
    Given a Submission ID, get the Submission object from metadata store.

    Args:
        submission_id: The Submission ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Runtime configuration

    Returns:
        The Submission object

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    submission = await collection.find_one({"id": submission_id})
    if submission and embedded:
        submission = await embed_references(submission, config, True)
    client.close()
    return Submission(**submission)


async def add_submission(
    input_submission: CreateSubmission, config: Config = CONFIG
) -> Dict:
    """
    Add a Submission object into metadata store.

    Args:
        submission: Submission object
        config: Runtime configuration

    """
    document = input_submission.dict()
    docs = await parse_document(document)
    docs = await link_embedded(docs)
    docs = await update_document(document, docs)
    await store_document(docs, config)

    submission = await embed_references(docs["parent"][1], config, True)

    return submission


async def insert_submission(submission: Submission, config: Config = CONFIG):
    """
    Store a Submission object into metadata store.

    Args:
        submission: Submission object
        config: Runtime configuration

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    await collection.insert_one(submission)
    client.close()


async def patch_submission(
    submission: Submission, status: SubmissionStatusPatch, config: Config = CONFIG
) -> Submission:
    """
    Updates a Submission object status.

    Args:
        submission: Submission object
        status: Submission status
        config: Runtime configuration

    """
    if (status.submission_status is not None) and (
        submission.submission_status != status.submission_status.value
    ):
        update_json = {}
        update_json["submission_status"] = status.submission_status.value
        update_json["update_date"] = await get_timestamp()
        submission = await update_submission_values(submission.id, update_json, config)

    return submission


async def update_submission_values(
    submission_id: str, update_json: Dict, config: Config = CONFIG
) -> Submission:
    """
    Updates a Submission object

    Args:
        submission_id: submission id
        update_json: values to be updated
        config: Runtime configuration

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    submission = await collection.find_one_and_update(
        {"id": submission_id},
        {"$set": update_json},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    client.close()

    return submission


async def update_submission(
    submission: Submission, input_submission: CreateSubmission, config: Config = CONFIG
) -> Dict:
    """
    Updates a Submission object into metadata store.

    Args:
        submission: Submission object to be updated
        input_submission: New submission object
        config: Runtime configuration

    """
    document = input_submission.dict()
    document["schema_type"] = "Submission"
    old_document = copy.deepcopy(submission.dict())
    await delete_document(old_document, "Submission", config=config)
    docs = await parse_document(document)
    docs = await link_embedded(docs)
    docs = await update_document(document, docs, old_document)
    await store_document(docs, config)
    updated_submission = await embed_references(docs["parent"][1], config, True)

    return updated_submission
