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
"Routes to support Submissions"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.creation_models import CreateSubmission
from metadata_repository_service.dao.submission import (
    add_submission,
    get_submission,
    patch_submission,
    update_submission,
)
from metadata_repository_service.models import Submission
from metadata_repository_service.patch_models import SubmissionStatusPatch

submission_router = APIRouter()


@submission_router.post(
    "/submissions",
    summary="Add a submission object to a metadata store",
    response_model=Submission,
    tags=["Submission"],
)
async def create_submission(
    input_submission: CreateSubmission, config: Config = Depends(get_config)
):
    """Add a submission object to a metadata store."""
    if input_submission is None:
        raise HTTPException(
            status_code=400,
            detail="Unexpected error",
        )

    submission = await add_submission(input_submission, config)
    return submission


@submission_router.get(
    "/submissions/{submission_id}",
    response_model=Submission,
    summary="Get a Submission",
    tags=["Query"],
)
async def get_submissions(
    submission_id: str, embedded: bool = False, config: Config = Depends(get_config)
):
    """
    Given a Submission ID, get the corresponding Submission record
    from the metadata store.
    """
    submission = await get_submission(
        submission_id=submission_id, embedded=embedded, config=config
    )
    if not submission:
        raise HTTPException(
            status_code=404,
            detail=f"{Submission.__name__} with id '{submission_id}' not found",
        )
    return submission


@submission_router.patch(
    "/submissions/{submission_id}",
    response_model=Submission,
    summary="Update the status of a submission",
    tags=["Submission"],
)
async def update_submission_status(
    submission_id: str,
    status: SubmissionStatusPatch,
    config: Config = Depends(get_config),
):
    """
    Given a Submission ID and a status, update the status of corresponding
    Submission record from the metadata store.
    """
    submission = await get_submission(
        submission_id=submission_id, embedded=False, config=config
    )
    if not submission:
        raise HTTPException(
            status_code=404,
            detail=f"{Submission.__name__} with id '{submission_id}' not found",
        )

    patched_submission = await patch_submission(submission, status, config)

    return patched_submission


@submission_router.put(
    "/submissions/{submission_id}",
    response_model=Submission,
    summary="Update the submission",
    tags=["Submission"],
)
async def update_full_submission(
    submission_id: str,
    input_submission: CreateSubmission,
    config: Config = Depends(get_config),
):
    """
    Given a Submission ID and an updated submission object,
    update the submission in the metadata store.
    """
    submission = await get_submission(
        submission_id=submission_id, embedded=False, config=config
    )
    if not submission:
        raise HTTPException(
            status_code=404,
            detail=f"{Submission.__name__} with id '{submission_id}' not found",
        )

    updated_submission = await update_submission(submission, input_submission, config)

    return updated_submission
