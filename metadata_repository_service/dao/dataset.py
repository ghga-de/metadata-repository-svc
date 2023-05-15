#!/usr/bin/env python3

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
Convenience methods for retrieving Dataset records
"""

from typing import List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.core.utils import generate_uuid, get_timestamp
from metadata_repository_service.creation_models import (
    CreateDataAccessPolicy,
    CreateDataset,
    CreateFile,
)
from metadata_repository_service.dao.analysis import get_analysis_by_linked_files
from metadata_repository_service.dao.data_access_policy import (
    get_data_access_policy_by_accession,
)
from metadata_repository_service.dao.dataset_embedded import (
    create_dataset_embedded_object,
    get_dataset_embedded,
)
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.experiment import get_experiments_by_linked_files
from metadata_repository_service.dao.file import get_file_by_accession
from metadata_repository_service.dao.sample import get_sample
from metadata_repository_service.dao.study import get_study
from metadata_repository_service.dao.utils import generate_accession, get_entity
from metadata_repository_service.models import Dataset
from metadata_repository_service.patch_models import (
    DatasetStatusPatch,
    ReleaseStatusEnum,
)

# pylint: disable=too-many-locals, too-many-statements, too-many-branches

COLLECTION_NAME = "Dataset"


async def retrieve_datasets(config: Config = CONFIG) -> List[str]:
    """
    Retrieve a list of Dataset object IDs from metadata store.

    Args:
        config: Rumtime configuration

    Returns:
        A list of Dataset object IDs.

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    datasets = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in datasets]


async def get_dataset(
    dataset_id: str, embedded: bool = False, config: Config = CONFIG
) -> Dataset:
    """
    Given a Dataset ID, get the Dataset object from metadata store.

    Args:
        dataset_id: The Dataset ID
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Dataset object

    """
    if not embedded:
        dataset = await get_entity(
            identifier=dataset_id,
            field="id",
            collection_name=COLLECTION_NAME,
            model_class=Dataset,
            embedded=False,
            config=config,
        )
        return dataset
    dataset_embedded = await get_dataset_embedded(dataset_id=dataset_id, config=config)
    if dataset_embedded is None:
        dataset = await get_entity(
            identifier=dataset_id,
            field="id",
            collection_name=COLLECTION_NAME,
            model_class=Dataset,
            embedded=True,
            config=config,
        )
        await create_dataset_embedded_object(dataset, config)
        dataset_embedded = await get_dataset_embedded(
            dataset_id=dataset_id, config=config
        )
        return dataset_embedded
    return dataset_embedded


async def get_dataset_by_accession(
    dataset_accession: str, embedded: bool = False, config: Config = CONFIG
) -> Dataset:
    """
    Given a Dataset accession, get the Dataset object from metadata store.

    Args:
        dataset_accession: The Dataset accession
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns:
        The Dataset object

    """
    dataset = await get_entity(
        identifier=dataset_accession,
        field="accession",
        collection_name=COLLECTION_NAME,
        model_class=Dataset,
        embedded=embedded,
        config=config,
    )
    return dataset


class DatasetError(RuntimeError):
    """Custom exception for Dataset"""


async def create_dataset(  # noqa: C901
    dataset: CreateDataset, config: Config = CONFIG
) -> Dataset:
    """
    Given a list of File IDs and a Data Access Policy ID, create a new Dataset object
    and write to the metadata store.

    Args:
        dataset: The Dataset object
        config: Rumtime configuration

    Returns:
        The Dataset object

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    # Get referenced File entities
    file_entities = {}
    for file_accession in dataset.has_file:
        if not file_accession:
            raise DatasetError("Dataset does not have a valid File: " f"{dataset}")
        if isinstance(file_accession, CreateFile):
            file_accession = file_accession.alias
        file_entity = await get_file_by_accession(
            file_accession=file_accession, config=config
        )
        if not file_entity:
            raise DatasetError(f"Cannot find a File with accession: {file_accession}")
        file_entities[file_entity.id] = file_entity

    dap_accession = dataset.has_data_access_policy
    if isinstance(dap_accession, CreateDataAccessPolicy):
        dap_accession = dap_accession.alias
    dap_entity = await get_data_access_policy_by_accession(dap_accession, config=config)
    if not dap_entity:
        raise DatasetError(
            "Cannot find a DataAccessPolicy with accession: "
            f"{dataset.has_data_access_policy}"
        )
    file_entity_id_list = list(file_entities.keys())

    experiment_entities = await get_experiments_by_linked_files(
        file_id_list=file_entity_id_list, config=config
    )

    # Get Sample entities that are linked to Experiment entities
    study_entities = {}
    sample_entities = {}
    for experiment in experiment_entities:
        if isinstance(experiment.has_study, str):
            study_entity = await get_study(experiment.has_study, config=config)
        else:
            study_entity = await get_study(experiment.has_study.id, config=config)
        study_entities[study_entity.id] = study_entity
        for sample in experiment.has_sample:
            if isinstance(sample, str):
                sample_entity = await get_sample(sample, config=config)
            else:
                sample_entity = await get_sample(sample.id, config=config)
            sample_entities[sample_entity.id] = sample_entity

    # Analysis
    analysis_entities = await get_analysis_by_linked_files(
        file_id_list=file_entity_id_list, config=config
    )
    for analysis in analysis_entities:
        if analysis.has_study:
            if isinstance(analysis.has_study, str):
                study_entity = await get_study(analysis.has_study, config=config)
            else:
                study_entity = await get_study(analysis.has_study.id, config=config)
            if study_entity.id not in study_entities:
                study_entities[study_entity.id] = study_entity

    # Dataset
    dataset_entity = dataset.dict()
    dataset_entity["id"] = await generate_uuid()
    dataset_entity["creation_date"] = await get_timestamp()
    dataset_entity["update_date"] = dataset_entity["creation_date"]
    dataset_entity["release_status"] = ReleaseStatusEnum.unreleased.value
    dataset_entity["accession"] = await generate_accession(
        COLLECTION_NAME, config=config
    )
    dataset_entity["has_file"] = file_entity_id_list
    dataset_entity["has_experiment"] = [x.id for x in experiment_entities]
    dataset_entity["has_analysis"] = [x.id for x in analysis_entities]
    dataset_entity["has_study"] = list(study_entities.keys())
    dataset_entity["has_sample"] = list(sample_entities.keys())
    dataset_entity["has_data_access_policy"] = dap_entity.id
    dataset_entity["schema_type"] = "Dataset"

    await collection.insert_one(dataset_entity)
    new_dataset = await get_dataset(dataset_entity["id"], config=config)
    return new_dataset


async def change_dataset_status(
    dataset_accession: str, dataset: DatasetStatusPatch, config: Config = CONFIG
) -> Dataset:
    """_summary_
    Given a Dataset accession, update its status.

    Args:
        dataset_accession: The Dataset accession
        dataset: The status of the dataset
        config: Rumtime configuration

    Returns:
        The Dataset object

    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]
    dataset_entity = await get_dataset_by_accession(dataset_accession, config=config)
    if dataset_entity.release_status != dataset.release_status:
        if dataset.release_status not in set(ReleaseStatusEnum):
            raise ValueError(
                f"dataset.release_status {dataset.release_status} not a valid value."
                + f" Must be one of {[x.value for x in ReleaseStatusEnum]}"
            )
        await collection.update_one(
            {"accession": dataset_accession},
            {
                "$set": {
                    "release_status": dataset.release_status,
                    "update_date": await get_timestamp(),
                }
            },
        )
        updated_dataset = await get_dataset(dataset_entity.id, config=config)
    else:
        updated_dataset = dataset_entity
    client.close()
    return updated_dataset
