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
Models corresponding to Dataset summary and Metadata summary
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Summary(BaseModel):
    """
    Summary
    """

    count: int = Field(None, description="""count of the summary item""")
    stats: Dict[str, Any] = Field(
        None,
        description="""a dictionary of stats for the summary item""",
    )


# pylint: disable=too-many-instance-attributes
class DatasetSummary(BaseModel):
    """
    Dataset summary
    """

    id: str = Field(None, description="""Dataset ID""")
    title: str = Field(None, description="""A title for the submitted Dataset.""")
    description: str = Field(None, description="""Description of the Dataset.""")
    accession: Optional[str] = Field(
        None, description="""GHGA Accession of the Dataset."""
    )
    ega_accession: Optional[str] = Field(
        None, description="""EGA Accession of the Dataset."""
    )
    type: List[str] = Field(None, description="""The type of the Dataset.""")
    dac_email: str = Field(None, description="""DAC contact email""")
    sample_summary: Summary = Field(None, description="Sample summary")
    study_summary: Summary = Field(None, description="Study summary")
    experiment_summary: Summary = Field(None, description="Experiment summary")
    file_summary: Summary = Field(None, description="File summary")


# pylint: disable=too-many-instance-attributes
class MetadataSummary(BaseModel):
    """
    Metadata summary
    """

    sample_summary: Summary = Field(None, description="Sample summary")
    file_summary: Summary = Field(None, description="File summary")
    experiment_summary: Summary = Field(None, description="Experiment summary")
    analysis_summary: Summary = Field(None, description="Analysis summary")
    individual_summary: Summary = Field(None, description="Individual summary")
    project_summary: Summary = Field(None, description="Project summary")
    protocol_summary: Summary = Field(None, description="Protocol summary")
    study_summary: Summary = Field(None, description="Study summary")
    biospecimen_summary: Summary = Field(None, description="Biospecimen summary")
    dataset_summary: Summary = Field(None, description="Dataset summary")
