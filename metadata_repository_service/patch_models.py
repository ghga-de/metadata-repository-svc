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
"""Models for patching objects"""

from typing import Optional

from pydantic import BaseModel, Field

from metadata_repository_service.models import ReleaseStatusEnum, SubmissionStatusEnum


class DatasetStatusPatch(BaseModel):
    """
    An object that can be used to change the release status of a Dataset.
    """

    release_status: Optional[ReleaseStatusEnum] = Field(
        None, description="The release status of a Dataset."
    )


class SubmissionStatusPatch(BaseModel):
    """
    An object that can be used to change the status of a Submission.
    """

    submission_status: Optional[SubmissionStatusEnum] = Field(
        None, description="The status of a Submission."
    )
