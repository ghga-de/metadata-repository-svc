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
Routes for retrieving Dataset Summary
"""

import logging
from collections import Counter

from fastapi import APIRouter, Depends

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.dataset import get_dataset
from metadata_repository_service.dao.dataset_summary import (
    create_dataset_summary_object,
    get_dataset_summary_object,
)
from metadata_repository_service.models import BiologicalSexEnum, SequencingProtocol
from metadata_repository_service.summary_models import DatasetSummary, Summary

log = logging.getLogger(__name__)

dataset_summary_router = APIRouter()


@dataset_summary_router.get(
    "/dataset_summary/{dataset_id}",
    response_model=DatasetSummary,
    summary="Get Dataset summary",
    tags=["Query"],
)
async def get_dataset_summary(dataset_id: str, config: Config = Depends(get_config)):
    """
    Given a Dataset ID, get the Dataset summary from the metadata store.
    """
    dataset_summary = await get_dataset_summary_object(
        dataset_id=dataset_id, config=config
    )
    if dataset_summary is None:
        dataset_summary = await create_dataset_summary(
            dataset_id=dataset_id, embedded=True, config=config
        )
    return dataset_summary


async def create_dataset_summary(
    dataset_id: str, embedded: bool, config: Config = Depends(get_config)
):
    """
    create dataset summary for the given dataset and write to metadata store
    """
    dataset = await get_dataset(dataset_id=dataset_id, embedded=embedded, config=config)
    dataset_summary = DatasetSummary()
    dataset_summary.id = dataset.id
    dataset_summary.title = dataset.title
    dataset_summary.ega_accession = dataset.ega_accession
    dataset_summary.accession = dataset.accession
    dataset_summary.description = dataset.description
    dataset_summary.type = dataset.type
    dataset_summary.dac_email = get_dac_email(dataset.has_data_access_policy)

    dataset_summary.sample_summary = get_sample_summary(dataset.has_sample)
    dataset_summary.study_summary = get_study_summary(dataset.has_study)
    dataset_summary.experiment_summary = get_experiment_summary(dataset.has_experiment)
    dataset_summary.file_summary = get_file_summary(dataset.has_file)

    new_dataset_summary = await create_dataset_summary_object(dataset_summary)
    return new_dataset_summary


def get_dac_email(data_access_policy):
    """
    This method returns the email ids of the DAC members

    Args:
        data_access_policy (data_access_policy): data_access_policy
    """
    dac_email = ""
    if data_access_policy is not None:
        if data_access_policy.has_data_access_committee is not None:
            if data_access_policy.has_data_access_committee.has_member is not None:
                members = data_access_policy.has_data_access_committee.has_member
    for member in members:
        if member.email is not None:
            dac_email += member.email + ";"
    return dac_email


def get_sample_summary(sample):
    """
    Sample Summary

    Args:
        sample (Sample): sample
    """
    sample_summary = Summary()
    if sample is None:
        sample_summary.count = 0
        sample_summary.stats = {}
    else:
        count = len(sample)
        sample_summary.count = count
        sample_summary.stats = get_sample_summary_stats(sample)
    return sample_summary


# flake8: noqa: C901
def get_sample_summary_stats(sample):
    """A method to get sample summary stats

    Args:
        sample (Sample): sample

    Returns:
        stats: a dictionary of stats
    """
    stats = {}
    male = 0
    female = 0
    unknown = 0
    tissues = []
    phenotypes = []
    for samp in sample:
        for ind in samp.has_individual:
            if ind[0] == "sex":
                if ind[1] == BiologicalSexEnum.male:
                    male = male + 1
                if ind[1] == BiologicalSexEnum.female:
                    female = female + 1
                if ind[1] == BiologicalSexEnum.unknown:
                    unknown = unknown + 1
            if ind[0] == "has_phenotypic_feature":
                if ind[1] is not None:
                    for item in ind[1]:
                        phenotypes.append(item.concept_name)
        for anotomical_entity in samp.has_anatomical_entity:
            tissues.append(anotomical_entity.concept_name)
    sex_count = {"male": male, "female": female, "unkown": unknown}
    stats = {
        "sex": sex_count,
        "tissues": Counter(tissues),
        "phenotypes": Counter(phenotypes),
    }
    return stats


def get_study_summary(study):
    """
    Study Summary

    Args:
        study (Study): study
    """

    study_summary = Summary()
    if study is None:
        study_summary.count = 0
        study_summary.stats = {}
    else:
        study_summary.count = len(study)
        for item in study:
            study_summary.stats = {
                "ega_accession": item.ega_accession,
                "accession": item.accession,
                "title": item.title,
            }
    return study_summary


def get_experiment_summary(experiment):
    """
    Experiment Summary

    Args:
        experiment (Experiment): experiment
    """

    experiment_summary = Summary()
    protocols_list = []
    if experiment is None:
        experiment_summary.count = 0
        experiment_summary.stats = {}
    else:
        experiment_summary.count = len(experiment)

        for exp in experiment:
            for protocol in exp.has_protocol:
                if isinstance(protocol, SequencingProtocol):
                    protocols_list.append(protocol.instrument_model)
        experiment_summary.stats = {"protocol": Counter(protocols_list)}
    return experiment_summary


def get_file_summary(file):
    """
    File Summary

    Args:
        file (File): file
    """

    file_summary = Summary()
    if file is None:
        file_summary.count = 0
        file_summary.stats = {}
    else:
        file_summary.count = len(file)
        file_size = 0
        file_format_list = []
        for fil in file:
            file_format_list.append(fil.format)
            if fil.size is not None:
                file_size += fil.size
        file_summary.stats = {"format": Counter(file_format_list), "size": file_size}
    return file_summary
