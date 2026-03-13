# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import time as tm

from pydantic import BaseModel
from pydantic import Field


class MessagePayload(BaseModel):
    project: str = 'project'
    file_id: str
    job_id: str
    session_id: str
    operator: str
    access_token: str
    destination_api_url: str
    destination_project_code: str
    destination_access_token: str


class Message(BaseModel):
    create_timestamp: float = Field(default_factory=tm.time)
    event_type: str
    payload: MessagePayload
