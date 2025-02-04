# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.11

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
# Install python packages

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

# Copy local code to the container image.
COPY . .

ENV HOST 0.0.0.0

EXPOSE 8080

# Run the web service on container startup
ENTRYPOINT ["streamlit", "run", "Home.py","--server.port=8080", "--server.address=0.0.0.0"]