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
Convenience methods for retrieving Dataset summary
"""

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.dataset_summary import get_summary_dict
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.summary_models import MetadataSummary

# pylint: disable=too-many-locals, too-many-statements, too-many-branches
COLLECTION_NAME = "MetadataSummary"


async def get_metadata_summary_object(config: Config = CONFIG) -> MetadataSummary:
    """
    Get the Metadata summary object from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        The Metadata Summary object

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    metadata_summary = await collection.find_one()
    return metadata_summary


async def create_metadata_summary_object(  # noqa: C901
    metadata_summary: MetadataSummary, config: Config = CONFIG
) -> MetadataSummary:
    """
    This method creates a metadata summary objects and write to MetadataSummary collection

    Args:
        metadata_summary:
        config :

    Returns:
        MetadataSummary
    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]

    metadata_summary_entity = metadata_summary.dict()
    metadata_summary_entity["dataset_summary"] = get_summary_dict(
        metadata_summary.dataset_summary
    )
    metadata_summary_entity["file_summary"] = get_summary_dict(
        metadata_summary.file_summary
    )
    metadata_summary_entity["individual_summary"] = get_summary_dict(
        metadata_summary.individual_summary
    )
    metadata_summary_entity["protocol_summary"] = get_summary_dict(
        metadata_summary.protocol_summary
    )

    await collection.insert_one(metadata_summary_entity)
    new_dataset_summary = await get_metadata_summary_object(config=config)
    return new_dataset_summary
