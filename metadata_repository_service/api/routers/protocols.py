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
"Routes for retrieving Protocols"

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from metadata_repository_service.api.deps import get_config
from metadata_repository_service.config import Config
from metadata_repository_service.dao.protocol import get_protocol
from metadata_repository_service.models import AnnotatedProtocol, Protocol

protocol_router = APIRouter()


@protocol_router.get(
    "/protocols/{protocol_id}",
    response_model=AnnotatedProtocol,
    summary="Get a Protocol",
    tags=["Query"],
)
async def get_protocols(
    protocol_id: str, embedded: bool = False, config: Config = Depends(get_config)
):
    """
    Given a Protocol ID, get the Protocol record from the metadata store.
    """
    protocol = await get_protocol(
        protocol_id=protocol_id, embedded=embedded, config=config
    )
    if not protocol:
        raise HTTPException(
            status_code=404,
            detail=f"{Protocol.__name__} with id '{protocol_id}' not found",
        )
    return protocol
