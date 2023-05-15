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

"""Config Parameter Modeling and Parsing"""

import logging.config

from ghga_service_chassis_lib.api import ApiConfigBase
from ghga_service_chassis_lib.config import config_from_yaml


def configure_logging():
    """Configure the application logging.

    This must happen before the application is configured.
    """
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(asctime)s %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "metadata_repository_service": {
                    "handlers": ["default"],
                    "level": CONFIG.log_level.upper(),
                },
            },
        }
    )


@config_from_yaml(prefix="metadata_repository_service")
class Config(ApiConfigBase):
    """Config parameters and their defaults."""

    # config parameter needed for the api server
    # are inherited from ApiConfigBase;
    # config parameter needed for the api server
    # are inherited from PubSubConfigBase;
    db_url: str = "mongodb://localhost:27017"
    db_name: str = "metadata-store"


CONFIG = Config()
