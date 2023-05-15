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
Submission through submission API
"""

import asyncio

import motor.motor_asyncio
import requests
import typer


async def populate_db():
    """
    Write embedded and summary datasets
    """
    datasets = await retrieve_datasets()
    for item in datasets:
        typer.echo(f"  - writing Embedded dataset {item} to DatasetEmbedded")
        response = requests.get(
            "http://localhost:8080/datasets/" + item + "?embedded=true"
        )
        if response.status_code == 200:
            typer.echo(f"  - writing dataset summary for {item} to DatasetSummary")
            response = requests.get("http://localhost:8080/dataset_summary/" + item)
            typer.echo(response.status_code)


async def retrieve_datasets():
    """
    retrieve a list of all datasets

    Returns:
        dataset_list: Dataset list
    """
    db_url: str = "mongodb://localhost:27017"
    db_name: str = "metadata-store"
    collection_name = "Dataset"
    client = motor.motor_asyncio.AsyncIOMotorClient(db_url)
    collection = client[db_name][collection_name]
    datasets = await collection.find().to_list(None)
    client.close()
    return [x["id"] for x in datasets]


def main():
    """main"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(populate_db())


if __name__ == "__main__":
    typer.run(main)
