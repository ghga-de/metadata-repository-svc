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
"""Dump records from the database for reach record type"""

import asyncio
import json
from os import makedirs

import motor
import motor.motor_asyncio
import typer
from populate_metadata_store import RECORD_TYPES


async def process_document(documents):
    """Process a set of documents"""
    for document in documents:
        del document["_id"]


async def get_records(db_url, db_name, collection_name):
    """Get all records for a given collection"""
    client = motor.motor_asyncio.AsyncIOMotorClient(db_url)
    collection = client[db_name][collection_name]
    documents = await collection.find().to_list(None)
    return documents


def main(
    db_url: str = "mongodb://localhost:27017",
    db_name: str = "metadata-store",
    output_dir: str = "output",
):
    """Get all records for all record types from the database"""
    loop = asyncio.get_event_loop()
    makedirs(output_dir, exist_ok=True)
    typer.echo(f"Dumping from {db_url} {db_name}")
    data = {}
    for record_type, collection_name in RECORD_TYPES:
        key = (record_type, collection_name)
        typer.echo(f"  - working on record type: {record_type}")
        documents = loop.run_until_complete(
            get_records(db_url, db_name, collection_name)
        )
        loop.run_until_complete(process_document(documents))
        data[key] = documents

    for key, values in data.items():
        record_type = key[0]
        collection_name = key[1]
        filename = f"{output_dir}/{record_type}.json"
        print(f"Writing {len(values)} {record_type} records to {filename}")
        with open(filename, "w", encoding="utf-8") as file:
            json.dump({record_type: values}, file, indent=4)


if __name__ == "__main__":
    typer.run(main)
