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
Convenience methods for retrieving Dataset Embedded
"""


from typing import Any, Dict, List

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.dao.db import get_db_client
from metadata_repository_service.dao.utils import embedded_fields, get_entity
from metadata_repository_service.models import Dataset

# pylint: disable=too-many-locals, too-many-statements, too-many-branches
COLLECTION_NAME = "DatasetEmbedded"


async def get_dataset_embedded(dataset_id: str, config: Config = CONFIG) -> Dataset:
    """
    Given a Dataset ID, get the Dataset embedded object from metadata store.

    Args:
        dataset_id: The Dataset ID
        config: Rumtime configuration

    Returns:
        The Dataset object

    """
    dataset_embedded = await get_entity(
        identifier=dataset_id,
        field="id",
        collection_name=COLLECTION_NAME,
        model_class=Dataset,
        embedded=False,
        config=config,
    )
    return dataset_embedded


async def create_dataset_embedded_object(
    dataset: Dataset, config: Config = CONFIG
) -> Dataset:
    """Create the embedded dataset and store it to database if not added before

    Args:
        dataset (Dataset): _description_
        config (Config, optional): _description_. Defaults to CONFIG.

    Returns:
        The final dataset with embedded objects
    """
    client = await get_db_client(config)
    collection = client[config.db_name][COLLECTION_NAME]

    dataset_dict = dataset.dict()
    dataset_embedded_entity = {}

    for field in dataset_dict:
        if field not in embedded_fields:
            dataset_embedded_entity[field] = dataset_dict[field]
        else:
            filters = {}
            if field == "has_experiment":
                filters["has_file"] = [file["id"] for file in dataset_dict["has_file"]]
                filters["has_sample"] = [
                    sample["id"] for sample in dataset_dict["has_sample"]
                ]
            dataset_embedded_entity[field] = get_embedded_entity_list(
                dataset_dict[field], filters
            )

    await collection.insert_one(dataset_embedded_entity)

    return Dataset(**dataset_embedded_entity)


def get_embedded_entity_list(entity_obj: Dict, filters: Dict) -> Dict:
    """Embed the full objects instead of reference in an entity / list of entities

    Args:
        entity_obj (Dict): the entity / list of entities to be extended
        filters (Dict): a list of ids to restrict the embedded objects

    Returns:
        The entity / list of entities with embedded objects
    """
    entity_list: List[Any] = []
    if entity_obj is None:
        return None
    if isinstance(entity_obj, list):
        for item in entity_obj:
            new_entity = {}
            for field in item:
                if field not in embedded_fields:
                    new_entity[field] = item[field]
                else:
                    if field in filters:
                        new_entity[field] = get_embedded_entity_list(
                            get_relevant_items(item[field], filters[field]), {}
                        )
                    else:
                        new_entity[field] = get_embedded_entity_list(item[field], {})
            entity_list.append(new_entity)
        return entity_list

    new_entity = {}
    for field in entity_obj:
        if field not in embedded_fields:
            new_entity[field] = entity_obj[field]
        else:
            new_entity[field] = get_embedded_entity_list(entity_obj[field], {})
    return new_entity


def get_relevant_items(items: List, item_list: List) -> List:
    """Select only the items from List which ids are included in the item_list

    Args:
        items (List): The whole list of items
        item_list (List): List of IDs to be retrieved

    Returns:
        The relevant items list

    """
    relevant_items_list = []
    if items is not None:
        for obj in items:
            if obj["id"] in item_list and obj["id"] not in relevant_items_list:
                relevant_items_list.append(obj)
    return relevant_items_list
