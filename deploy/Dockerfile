# -*- encoding: utf-8 -*-
# Copyright (c) 2023, TradingLab
# All rights reserved.
#
# This file is part of TradingLab.app
# See https://tradinglab.app for further info.
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

FROM python:3.11.4-slim-bullseye as prod
RUN apt-get update && apt-get install -y \
  default-libmysqlclient-dev \
  gcc \
  pkg-config \
  && rm -rf /var/lib/apt/lists/*

#WORKDIR /app/src

RUN pip install poetry==1.4.2

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN poetry install --only main
# Removing gcc
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copying actuall application
COPY . /app/src/
RUN poetry install --only main

CMD ["/usr/local/bin/python", "-m", "gryffen"]

FROM prod as dev

RUN poetry install
