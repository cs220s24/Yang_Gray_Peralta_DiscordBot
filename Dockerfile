# Copyright 2024 Fernando Peralta Castro
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

FROM amazonlinux

WORKDIR /app

# Install Python and pip
RUN yum -y update && yum -y install python3 python3-pip

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copies all files from local directory into Docker image at the /app directory
COPY . .

# Run bot.py when the container launches
CMD python3 bot.py
