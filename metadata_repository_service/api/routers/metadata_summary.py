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
Routes for retrieving Metadata Summary
"""

from collections import Counter

from fastapi import APIRouter, Depends

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.dataset import retrieve_datasets
from metadata_repository_service.dao.file import get_file_format, retrieve_files
from metadata_repository_service.dao.individual import (
    get_sex_count,
    retrieve_individuals,
)
from metadata_repository_service.dao.metadata_summary import (
    create_metadata_summary_object,
    get_metadata_summary_object,
)
from metadata_repository_service.dao.protocol import (
    get_instrument_model_count,
    retrieve_protocols,
)
from metadata_repository_service.summary_models import MetadataSummary, Summary

metadata_summary_router = APIRouter()


@metadata_summary_router.get(
    "/metadata_summary/",
    response_model=MetadataSummary,
    summary="Get Metadata summary",
    tags=["Query"],
)
async def get_metadata_summary(config: Config = Depends(get_config)):
    """
    Given a Dataset ID, get the Dataset summary from the metadata store.
    """
    metadata_summary = await get_metadata_summary_object(config=config)

    if metadata_summary is None:
        metadata_summary = await create_metadata_summary(config)
    return metadata_summary


async def create_metadata_summary(config: Config = Depends(get_config)):
    """_summary_

    Args:
        config (Config, optional): _description_. Defaults to Depends(get_config).
    """
    metadata_summary = MetadataSummary()
    metadata_summary.dataset_summary = await get_dataset_count_summary(config)
    metadata_summary.file_summary = await get_file_summary(config)
    metadata_summary.individual_summary = await get_individual_summary(config)
    metadata_summary.protocol_summary = await get_protocol_summary(config)

    new_metadata_summary = await create_metadata_summary_object(metadata_summary)
    return new_metadata_summary


async def get_dataset_count_summary(config: Config = Depends(get_config)):
    """
    Returns dataset count
    """
    dataset_summary = Summary()
    dataset_summary.count = len(await retrieve_datasets(config))
    dataset_summary.stats = {}
    return dataset_summary


async def get_file_summary(config: Config = Depends(get_config)):
    """
    Returns file count and stats
    """
    file_summary = Summary()
    file_summary.count = len(await retrieve_files(config))
    file_format_list = await get_file_format(config)
    file_summary.stats = {
        "format": Counter(item["format"] for item in file_format_list)
    }
    return file_summary


async def get_individual_summary(config: Config = Depends(get_config)):
    """
    Returns individual count and stats
    """
    individual_summary = Summary()
    individual_summary.count = len(await retrieve_individuals(config))
    sex_list = await get_sex_count(config)
    individual_summary.stats = {"sex": Counter(item["sex"] for item in sex_list)}
    return individual_summary


async def get_protocol_summary(config: Config = Depends(get_config)):
    """
    Returns Protocol count and stats
    """
    protocol_summary = Summary()
    protocol_summary.count = len(await retrieve_protocols(config))
    instument_model_list = await get_instrument_model_count(config)
    instument_model_list = [item for item in instument_model_list if bool(item)]
    protocol_summary.stats = {
        "protocol": Counter(item["instrument_model"] for item in instument_model_list)
    }
    return protocol_summary
