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
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import get_entity
from metadata_repository_service.summary_models import DatasetSummary, Summary

# pylint: disable=too-many-locals, too-many-statements, too-many-branches
COLLECTION_NAME = "DatasetSummary"


async def get_dataset_summary_object(
    dataset_id: str, config: Config = CONFIG
) -> DatasetSummary:
    """
    Given a Dataset ID, get the Dataset summary object from metadata store.

    Args:
        dataset_id: The Dataset ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Dataset object

    """
    dataset_summary = await get_entity(
        identifier=dataset_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=DatasetSummary,
        config=config,
    )
    return dataset_summary


async def create_dataset_summary_object(  # noqa: C901
    dataset_summary: DatasetSummary, config: Config = CONFIG
) -> DatasetSummary:
    """
    This method creates a dataset summary objects and write to DatasetSummary collection

    Args:
        dataset_summary:
        config :

    Returns:
        DatasetSummary
    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]

    dataset_summary_entity = dataset_summary.dict()
    dataset_summary_entity["id"] = dataset_summary.id
    dataset_summary_entity["title"] = dataset_summary.title
    dataset_summary_entity["ega_accession"] = dataset_summary.ega_accession
    dataset_summary_entity["accession"] = dataset_summary.accession
    dataset_summary_entity["description"] = dataset_summary.description
    dataset_summary_entity["type"] = dataset_summary.type
    dataset_summary_entity["dac_email"] = dataset_summary.dac_email

    dataset_summary_entity["sample_summary"] = get_summary_dict(
        dataset_summary.sample_summary
    )
    dataset_summary_entity["study_summary"] = get_summary_dict(
        dataset_summary.study_summary
    )
    dataset_summary_entity["experiment_summary"] = get_summary_dict(
        dataset_summary.experiment_summary
    )
    dataset_summary_entity["file_summary"] = get_summary_dict(
        dataset_summary.file_summary
    )

    await collection.insert_one(dataset_summary_entity)
    new_dataset_summary = await get_dataset_summary_object(
        dataset_summary_entity["id"], config=config
    )
    return new_dataset_summary


def get_summary_dict(summary: Summary):
    """
    This method converts the summary object into dict

    Args:
        summary (Summary): summary

    Returns:
        _type_: summary_dict
    """
    summary_dict = {"count": int, "stats": any}
    summary_dict["count"] = summary.count
    summary_dict["stats"] = summary.stats
    return summary_dict
