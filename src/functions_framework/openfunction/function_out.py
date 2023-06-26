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
class FunctionOut:
    def __init__(self, code: int, error, data, metadata):
        self.__code = code
        self.__error = error
        self.__data = data
        self.__metadata = metadata

    def __str__(self):
        return f"FunctionOut(code={self.__code}, error={self.__error}, data={self.__data}, metadata={self.__metadata})"

    def __repr__(self):
        return str(self)

    def set_code(self, code: int):
        self.__code = code

    def get_code(self) -> int:
        return self.__code

    def set_error(self, error):
        self.__error = error

    def get_error(self):
        return self.__error

    def set_data(self, data):
        self.__data = data

    def get_data(self):
        return self.__data

    def set_metadata(self, metadata):
        self.__metadata = metadata

    def get_metadata(self):
        return self.__metadata
