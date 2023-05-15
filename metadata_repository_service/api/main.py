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
Module containing the main FastAPI router and (optionally) top-level API enpoints.
Additional endpoints might be structured in dedicated modules
(each of them having a sub-router).
"""

from fastapi import FastAPI
from ghga_service_chassis_lib.api import configure_app

from metadata_repository_service.api.routers.analyses import analysis_router
from metadata_repository_service.api.routers.analysis_processes import (
    analysis_process_router,
)
from metadata_repository_service.api.routers.biospecimens import biospecimen_router
from metadata_repository_service.api.routers.data_access_committees import (
    data_access_committee_router,
)
from metadata_repository_service.api.routers.data_access_policies import (
    data_access_policy_router,
)
from metadata_repository_service.api.routers.dataset_summary import (
    dataset_summary_router,
)
from metadata_repository_service.api.routers.datasets import dataset_router
from metadata_repository_service.api.routers.experiment_processes import (
    experiment_process_router,
)
from metadata_repository_service.api.routers.experiments import experiment_router
from metadata_repository_service.api.routers.files import file_router
from metadata_repository_service.api.routers.individuals import individual_router
from metadata_repository_service.api.routers.members import member_router
from metadata_repository_service.api.routers.metadata_summary import (
    metadata_summary_router,
)
from metadata_repository_service.api.routers.projects import project_router
from metadata_repository_service.api.routers.protocols import protocol_router
from metadata_repository_service.api.routers.publications import publication_router
from metadata_repository_service.api.routers.samples import sample_router
from metadata_repository_service.api.routers.studies import study_router
from metadata_repository_service.api.routers.submissions import submission_router
from metadata_repository_service.api.routers.technologies import technology_router
from metadata_repository_service.api.routers.workflows import workflow_router
from metadata_repository_service.config import CONFIG, configure_logging

configure_logging()

app = FastAPI()
configure_app(app, config=CONFIG)

app.include_router(dataset_router)
app.include_router(analysis_router)
app.include_router(analysis_process_router)
app.include_router(biospecimen_router)
app.include_router(data_access_committee_router)
app.include_router(data_access_policy_router)
app.include_router(experiment_process_router)
app.include_router(experiment_router)
app.include_router(file_router)
app.include_router(individual_router)
app.include_router(member_router)
app.include_router(project_router)
app.include_router(protocol_router)
app.include_router(publication_router)
app.include_router(sample_router)
app.include_router(study_router)
app.include_router(submission_router)
app.include_router(technology_router)
app.include_router(workflow_router)
app.include_router(dataset_summary_router)
app.include_router(metadata_summary_router)


@app.get("/")
async def index():
    """
    Index of the Metadata Repository Service that
    redirects to the API documentation.
    """
    return "Index of the Metadata Repository Service"
