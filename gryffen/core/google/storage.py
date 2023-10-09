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

import os
import json
import logging
from dotenv import load_dotenv
from google.cloud import storage
from google.cloud.exceptions import NotFound


load_dotenv()


class Storage:

    """
    Storage class for Gryffen.

    Attributes:
        bucket_name: Name of the bucket.
        credentials: Credentials for the storage client.
        storage_client: Storage client.
        bucket: Bucket object.

    Methods:
        init_storage: Initialize storage client.
        upload_file: Upload file to storage.
        download_file: Download file from storage.
        delete_file: Delete file from storage.
        list_files: List files in storage.
        get_file_metadata: Get file metadata from storage.
        set_file_metadata: Set file metadata in storage.
    """

    def __init__(self, bucket_name: str):
        """
        Constructor for Storage class.
        """
        self.bucket_name = bucket_name
        self.credentials = os.getenv("SERVICE_ACCOUNT_JSON")
        self.storage_client = None
        self.bucket = None

    async def init_storage(self) -> None:
        """
        Initialize storage client.
        """
        service_account_json_string = os.getenv("SERVICE_ACCOUNT_JSON")
        self.storage_client = storage.Client.from_service_account_info(
            info=json.loads(service_account_json_string)
        )
        # Creating the bucket if it does not exist
        if not self._is_bucket_exists(self.bucket_name):
            logging.info(
                f"Storage client initialized, and bucket {self.bucket_name} "
                f"does not exists. Creating bucket"
            )
            _bucket = self.storage_client.bucket(self.bucket_name)
            _bucket.storage_class = 'STANDARD'
            self.bucket = self.storage_client.create_bucket(
                _bucket, location='us-central1'
            )
            logging.info(
                f"Storage client initialized, and bucket {self.bucket.name} "
                f"is successfully created."
            )

    async def _is_bucket_exists(self, bucket_name) -> bool:
        """
        Check if bucket exists.
        """
        try:
            self.storage_client.get_bucket(bucket_name)
            return True
        except NotFound:
            return False

    async def upload_file(self, file_path: str, file_name: str) -> None:
        """
        Upload file to storage.
        """
        blob = self.bucket.blob(file_name)
        blob.upload_from_filename(file_path)
        logging.info("File uploaded to storage.")

    async def download_file(self, file_name: str, file_path: str):
        """
        Download file from storage.
        """
        blob = self.bucket.blob(file_name)
        blob.download_to_filename(file_path)
        logging.info("File downloaded from storage.")

    async def delete_file(self, file_name: str):
        """
        Delete file from storage.
        """
        blob = self.bucket.blob(file_name)
        blob.delete()
        logging.info("File deleted from storage.")

    async def list_files(self):
        """
        List files in storage.
        """
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            logging.info(blob.name)

    async def get_file_metadata(self, file_name: str):
        """
        Get file metadata from storage.
        """
        blob = self.bucket.get_blob(file_name)
        return blob.metadata

    async def set_file_metadata(self, file_name: str, metadata) -> None:
        """
        Set file metadata in storage.
        """
        blob = self.bucket.get_blob(file_name)
        blob.metadata = metadata
        blob.patch()
        logging.info("File metadata set in storage.")

    async def get_file_content(self, file_name: str):
        """
        Get file content from storage.
        """
        blob = self.bucket.get_blob(file_name)
        return blob.download_as_string()

    async def set_file_content(self, file_name: str, content) -> None:
        """
        Set file content in storage.
        """
        blob = self.bucket.get_blob(file_name)
        blob.upload_from_string(content)
        logging.info("File content set in storage.")

    async def get_file_content_as_json(self, file_name: str):
        """
        Get file content as JSON from storage.
        """
        blob = self.bucket.get_blob(file_name)
        return json.loads(blob.download_as_string())

    async def set_file_content_as_json(self, file_name: str, content) -> None:
        """
        Set file content as JSON in storage.
        """
        blob = self.bucket.get_blob(file_name)
        blob.upload_from_string(json.dumps(content))
        logging.info("File content set in storage.")

    async def get_file_content_as_bytes(self, file_name: str):
        """
        Get file content as bytes from storage.
        """
        blob = self.bucket.get_blob(file_name)
        return blob.download_as_bytes()

    async def set_file_content_as_bytes(self, file_name: str, content) -> None:
        """
        Set file content as bytes in storage.
        """
        blob = self.bucket.get_blob(file_name)
        blob.upload_from_bytes(content)
        logging.info("File content set in storage.")

    async def get_file_content_as_string(self, file_name: str):
        """
        Get file content as string from storage.
        """
        blob = self.bucket.get_blob(file_name)
        return blob.download_as_string()

    async def set_file_content_as_string(self, file_name: str, content):
        """
        Set file content as string in storage.
        """
        blob = self.bucket.get_blob(file_name)
        blob.upload_from_string(content)
        logging.info("File content set in storage.")

    async def get_file_content_as_stream(self, file_name: str):
        """
        Get file content as stream from storage.
        """
        blob = self.bucket.get_blob(file_name)
        return blob.download_as_stream()

    async def set_file_content_as_stream(self, file_name: str, content) -> None:
        """
        Set file content as stream in storage.
        """
        blob = self.bucket.get_blob(file_name)
        blob.upload_from_stream(content)
        logging.info("File content set in storage.")

    async def get_file_content_as_file(self, file_name: str, file_path: str):
        """
        Get file content as file from storage.
        """
        blob = self.bucket.get_blob(file_name)
        blob.download_to_filename(file_path)
        logging.info("File content set in storage.")

    async def set_file_content_as_file(
        self, file_name: str, file_path: str
    ) -> None:
        """
        Set file content as file in storage.
        """
        blob = self.bucket.get_blob(file_name)
        blob.upload_from_filename(file_path)
        logging.info("File content set in storage.")

    async def get_file_content_as_file_object(
        self, file_name: str
    ):
        """
        Get file content as file object from storage.
        """
        blob = self.bucket.get_blob(file_name)
        return blob.download_as_file_object()

    async def set_file_content_as_file_object(
        self, file_name: str, file_object
    ) -> None:
        """Set file content as file object in storage.

        Args:
            file_name:
            file_object:

        Returns:
        """
        blob = self.bucket.get_blob(file_name)
        blob.upload_from_file_object(file_object)
        logging.info("File content set in storage.")
