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
"""Utility methods for DAO"""

# pylint: disable=too-many-arguments

import copy
import logging
import random
from typing import Any, Dict, List, Set

import stringcase

from metadata_repository_service.config import CONFIG, Config
from metadata_repository_service.core.utils import generate_uuid, get_timestamp
from metadata_repository_service.dao.db import get_db_client

embedded_fields: Set = {
    "has_analysis",
    "has_analysis_process",
    "has_biospecimen",
    "has_data_access_committee",
    "has_data_access_policy",
    "has_dataset",
    "has_experiment_process",
    "has_experiment",
    "has_file",
    "has_individual",
    "has_member",
    "has_project",
    "has_protocol",
    "has_publication",
    "has_sample",
    "has_study",
    "has_workflow",
}


ACCESSIONED_ENTITIES = {
    "Dataset",
    "Study",
    "Project",
    "Sample",
    "Biospecimen",
    "Individual",
    "Experiment",
    "File",
    "Analysis",
    "DataAccessPolicy",
    "DataAccessCommittee",
}


async def _get_reference(
    document_id: str, collection_name: str, config: Config = CONFIG
) -> Dict:
    """Given a document ID and a collection name, query the metadata store
    and return the document.

    Args:
        document_id: The ID of the document
        collection_name: The collection in the metadata store that has the document

    Returns
        The document corresponding to ``document_id``

    """
    client = await get_db_client(config)
    collection = client[config.db_name][collection_name]
    doc = await collection.find_one({"id": document_id})
    if not doc:
        logging.warning(
            "Reference with ID %s not found in collection %s",
            document_id,
            collection_name,
        )
    return doc


async def get_entity(
    identifier: str,
    field: str,
    collection_name: str,
    model_class: Any = None,
    embedded: bool = False,
    config: Config = CONFIG,
) -> Any:
    """
    Given an identifier, field name and collection name, look up the
    identifier in the provided field of a collection and return the
    corresponding document.

    Args:
        identifier: The identifier
        field: The name of the field
        collection_name: The collection in the metadata store that has the document
        model_class: The model class
        embedded: Whether or not to embed references. ``False``, by default.
        config: Rumtime configuration

    Returns
        The document

    """
    client = await get_db_client(config)
    collection = client[config.db_name][collection_name]
    entity = await collection.find_one({field: identifier})
    if entity and embedded:
        entity = await embed_references(entity, config=config)
    client.close()
    if model_class and entity:
        entity_obj = model_class(**entity)
    else:
        entity_obj = entity
    return entity_obj


async def get_schema_type(
    identifier: str,
    field: str,
    collection_name: str,
    property_name: str,
    config: Config = CONFIG,
) -> str:
    """
    Given an identifier, field name and collection name, return the property,
    e.g. schema type of the object.

    Args:
        identifier: The identifier
        field: The name of the field
        collection_name: The collection in the metadata store that has the document
        property_name: The name of the property to return
        config: Rumtime configuration

    Returns
        The value of the property

    """
    client = await get_db_client(config)
    collection = client[config.db_name][collection_name]
    entity = await collection.find_one({field: identifier})
    return entity[property_name]


async def embed_references(
    document: Dict, config: Config = CONFIG, only_top_level: bool = False
) -> Dict:
    """Given a document and a document type, identify the references in ``document``
    and query the metadata store. After retrieving the referenced objects,
    embed them in place of the reference in the parent document.

    Args:
        document: The document that has one or more references

    Returns
        The denormalize/embedded document

    """
    parent_document = copy.deepcopy(document)
    for field in parent_document.keys():
        if field.startswith("has_") and field not in {"has_attribute"}:
            if field not in embedded_fields:
                continue
            cname = field.split("_", 1)[1]
            formatted_cname = stringcase.pascalcase(cname)
            if isinstance(parent_document[field], str):
                referenced_doc = await get_referenced_doc(
                    parent_document[field],
                    formatted_cname,
                    config=config,
                    only_top_level=only_top_level,
                )
                parent_document[field] = referenced_doc
            elif isinstance(parent_document[field], (list, set, tuple)):
                docs = []
                for ref in parent_document[field]:
                    referenced_doc = await get_referenced_doc(
                        ref,
                        formatted_cname,
                        config=config,
                        only_top_level=only_top_level,
                    )
                    docs.append(referenced_doc)
                if docs:
                    parent_document[field] = docs
    return parent_document


async def get_referenced_doc(
    ref: str,
    collection_name: str,
    config: Config = CONFIG,
    only_top_level: bool = False,
) -> Dict:
    """Retrieve the referenced document"""
    referenced_doc = await _get_reference(ref, collection_name, config=config)
    if referenced_doc:
        if not only_top_level:
            referenced_doc = await embed_references(referenced_doc, config=config)
    return referenced_doc


async def generate_accession(collection_name: str, config: Config = CONFIG) -> str:
    """
    Generate a unique accession.

    The uniqueness of the accession is ensured by checking the metadata store
    to see if a generated accession already exists.

    Args:
        collection_name: The name of the collection
        config: Runtime configuration

    Returns:
        A new accession

    """
    client = await get_db_client(config)
    collection = client[config.db_name]["_accession_tracker_"]
    accession = await _generate_accession(collection_name=collection_name)
    accession_tracker_obj = await collection.find_one({"accession": accession})
    if accession_tracker_obj:
        accession = await generate_accession(
            collection_name=collection_name, config=config
        )
    else:
        accession_tracker_obj = {
            "accession": accession,
            "timestamp": await get_timestamp(),
        }
        await collection.insert_one(accession_tracker_obj)
    client.close()
    return accession


async def _generate_accession(collection_name: str) -> str:
    """
    Generate an accession for a collection.

    Args:
        collection_name: The name of the collection

    Returns:
        A new accession

    """
    special_accession_prefix = {
        "DataAccessPolicy": "DAP",
        "DataAccessCommittee": "DAC",
    }
    reference = random.randint(1, 999_999_999_999)  # nosec
    if collection_name in special_accession_prefix:
        collection_abbr = special_accession_prefix.get(collection_name)
    else:
        collection_abbr = collection_name[:3].upper()
    accession = f"GHGA:{collection_abbr}{str(reference).zfill(12)}"
    return accession


async def parse_document(document: Dict) -> Dict:
    """Given a document, identify the embeded documents and extract them
    as the separate documents. Add the identifier and creation/update date to each
    of the objects.

    Args:
        document: The original document

    Returns
        The dictionary of embedded documents with alias as a key

    """
    embedded_docs = {}
    for field in document.keys():
        if field.startswith("has_") and field not in {"has_attribute"}:
            if field not in embedded_fields:
                continue
            cname = field.split("_", 1)[1]
            formatted_cname = stringcase.pascalcase(cname)
            if document[field] is None:
                continue
            if not isinstance(document[field], list):
                doc = document[field]
                embedded_docs[doc["alias"]] = (
                    formatted_cname,
                    await add_create_fields(doc),
                )
            else:
                for doc in document[field]:
                    embedded_docs[doc["alias"]] = (
                        formatted_cname,
                        await add_create_fields(doc),
                    )

    return embedded_docs


async def link_embedded(docs: Dict) -> Dict:
    """Given a dictionary of embedded documents linked by the alias,
    substitute the alias references by UUID references.

    Args:
        docs: The dictionary of documents linked by alias

    Returns
        The dictionary of documents linked by UUID ids

    """

    for alias in docs.keys():
        (doc_type, doc) = docs[alias]
        for field in doc.keys():
            if field.startswith("has_") and field not in {"has_attribute"}:
                if field not in embedded_fields:
                    continue
                doc[field] = await replace_reference(doc[field], docs)
        docs[alias] = (doc_type, doc)

    return docs


async def replace_reference(reference, docs: Dict) -> Dict:
    """Given a reference/list of references via aliases ,
    substitute the alias references by UUID references.

    Args:
        reference: Reference by alias
        docs: The dictionary of documents linked by alias

    Returns
        References by UUID ids

    """
    new_reference = reference
    if isinstance(reference, str):
        if reference in docs.keys():
            (_, referenced_doc) = docs[reference]
            new_reference = referenced_doc["id"]
    elif isinstance(reference, list):
        new_list = []
        for ref in reference:
            if ref in docs.keys():
                (_, referenced_doc) = docs[ref]
                new_list.append(referenced_doc["id"])
        new_reference = new_list

    return new_reference


async def update_document(parent_document, docs: Dict, old_document=None) -> Dict:
    """Given a parent document and a dictionary of embedded documents,
    update the embedded documents within the parent one,
    then add the parent document to the dictionary.

    Args:
        parent_document: The parent document

    Returns
        The dictionary of all documents (parent and embedded documents)

    """
    if old_document is None:
        parent_document = await add_create_fields(parent_document)
        parent_document["submission_status"] = "in_progress"
    else:
        parent_document = await add_update_fields(parent_document, old_document)
        parent_document["submission_status"] = old_document["submission_status"]

    for field in parent_document.keys():
        if field.startswith("has_") and field not in {"has_attribute"}:
            if field not in embedded_fields:
                continue
            if parent_document[field] is None:
                continue
            if not isinstance(parent_document[field], list):
                doc = parent_document[field]
                if not isinstance(doc, Dict):
                    doc = doc.dict()
                (_, referenced_doc) = docs[doc["alias"]]
                parent_document[field] = referenced_doc["id"]
            else:
                new_list = []
                for doc in parent_document[field]:
                    if not isinstance(doc, Dict):
                        doc = doc.dict()
                    (_, referenced_doc) = docs[doc["alias"]]
                    new_list.append(referenced_doc["id"])
                parent_document[field] = new_list
    docs["parent"] = ["Submission", parent_document]
    return docs


async def delete_document(
    parent_document: Dict, parent_cname: str, config: Config = CONFIG
):
    """Deletes a parent document together with embedded documents from the database.

    Args:
        parent_document: The parent document

    """

    client = await get_db_client(config)

    collection = client[config.db_name][parent_cname]
    collection.delete_one({"id": parent_document["id"]})

    for field in parent_document.keys():
        if field.startswith("has_") and field not in {"has_attribute"}:
            if field not in embedded_fields:
                continue
            if parent_document[field] is None:
                continue
            cname = field.split("_", 1)[1]
            formatted_cname = stringcase.pascalcase(cname)
            collection = client[config.db_name][formatted_cname]
            if not isinstance(parent_document[field], list):
                doc_id = parent_document[field]
                await collection.delete_one({"id": doc_id})
            else:
                for doc_id in parent_document[field]:
                    await collection.delete_one({"id": doc_id})

    client.close()


async def store_document(docs: Dict, config: Config = CONFIG):
    """
    Stores submission documents to metadata store


    Args:
        docs: Dictionary of documents to be stored

    """

    records: Dict[str, List] = {}
    for key in docs.keys():
        (cname, record) = docs[key]
        if cname not in records:
            records[cname] = []
        records[cname].append(record)

    client = await get_db_client(config)
    for key, record_list in records.items():
        if key in ACCESSIONED_ENTITIES:
            for record in record_list:
                if "accession" in record and record["accession"]:
                    continue
                accession = await generate_accession(collection_name=key, config=config)
                record["accession"] = accession

    for key, record_list in records.items():
        collection = client[config.db_name][key]
        if len(record_list) == 1:
            await collection.insert_one(record_list[0])
        else:
            await collection.insert_many(record_list)

    client.close()


async def add_create_fields(document: Dict) -> Dict:
    """Add uuid identifier and create/update date to a document

     Args:
        document: Original document

    Returns
        Annotated document

    """
    if not isinstance(document, Dict):
        document = document.__dict__
    document["id"] = await generate_uuid()
    document["creation_date"] = await get_timestamp()
    document["update_date"] = document["creation_date"]
    if document["schema_type"].startswith("Create"):
        document["schema_type"] = document["schema_type"].replace("Create", "", 1)
    for field in document.keys():
        if (
            field.startswith("has_")
            and field not in {"has_attribute"}
            and field not in embedded_fields
        ):
            if document[field] is None:
                continue
            if not isinstance(document[field], list):
                if not isinstance(document[field], str):
                    document[field] = await add_create_fields(document[field])
            else:
                if not isinstance(document[field][0], str):
                    new_list = []
                    for doc in document[field]:
                        doc = await add_create_fields(doc)
                        new_list.append(doc)
                    document[field] = new_list
    return document


async def add_update_fields(document, old_document: Dict) -> Dict:
    """Add current update date to a document,
    uuid and create date are taken from the original document

     Args:
        document: Original document

    Returns
        Annotated document

    """
    document["id"] = old_document["id"]
    document["creation_date"] = old_document["creation_date"]
    document["update_date"] = await get_timestamp()
    return document
