# Copyright 2023 The OpenFunction Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging


def initialize_logger(name=None, level=logging.DEBUG):
    if not name:
        name = __name__
    _logger = logging.getLogger(name)

    # set logger level
    _logger.setLevel(level)

    # create file handler
    file_handler = logging.FileHandler("function.log")
    file_handler.setLevel(level)

    # create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # add handlers to logger
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger


# initialize logger
logger = initialize_logger(__name__, logging.INFO)
