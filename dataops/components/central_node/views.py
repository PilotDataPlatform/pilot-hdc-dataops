# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from http import HTTPStatus

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response

from dataops.components.authorization import Authorization
from dataops.components.central_node.device_storage import DeviceStorage
from dataops.components.central_node.device_storage import UploadData
from dataops.components.central_node.device_storage import get_device_storage
from dataops.components.central_node.keycloak import KeycloakClient
from dataops.components.central_node.keycloak import KeycloakDeviceAuthError
from dataops.components.central_node.keycloak import get_keycloak_client
from dataops.components.central_node.models import Message
from dataops.components.central_node.models import MessagePayload
from dataops.components.central_node.schemas import FileUploadResponseSchema
from dataops.components.central_node.schemas import FileUploadSchema
from dataops.components.resource_operations.dependencies import get_resource_ops_auth
from dataops.config import Settings
from dataops.config import get_settings
from dataops.services.queue import QueueService
from dataops.services.queue import get_queue_service

router = APIRouter(prefix='/central-node')


@router.post('/upload', response_model=FileUploadResponseSchema)
async def init_file_upload(
    data: FileUploadSchema,
    keycloak_client: KeycloakClient = Depends(get_keycloak_client),
    device_storage: DeviceStorage = Depends(get_device_storage),
) -> FileUploadResponseSchema:
    try:
        device_auth = await keycloak_client.init_device_auth()
    except KeycloakDeviceAuthError as exc:
        raise HTTPException(status_code=400, detail='Unable to init file upload') from exc

    upload_key = await device_storage.save_upload_data(
        data=UploadData(
            file_id=data.file_id,
            project_code=data.project_code,
            job_id=data.job_id,
            session_id=data.session_id,
            operator=data.operator,
            device_code=device_auth.device_code,
        ),
        ttl_seconds=device_auth.expires_in,
    )

    return FileUploadResponseSchema(upload_key=upload_key, login_url=device_auth.verification_uri_complete)


@router.get('/upload/{upload_key}')
async def wait_for_file_upload_authorization(
    upload_key: str,
    keycloak_client: KeycloakClient = Depends(get_keycloak_client),
    device_storage: DeviceStorage = Depends(get_device_storage),
    queue_service_client: QueueService = Depends(get_queue_service),
    current_identity: Authorization = Depends(get_resource_ops_auth),
    settings: Settings = Depends(get_settings),
) -> Response:
    access_token = await current_identity.jwt_required()

    upload_data = await device_storage.get_upload_data(upload_key)
    if upload_data is None:
        raise HTTPException(status_code=404, detail='Unknown or expired upload key')

    try:
        token_response = await keycloak_client.wait_for_device_auth(upload_data.device_code)
    except KeycloakDeviceAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=408, detail=str(exc)) from exc

    message = Message(
        event_type='copy_to_central_node',
        payload=MessagePayload(
            file_id=str(upload_data.file_id),
            destination_api_url=settings.CENTRAL_NODE_API_URL,
            destination_project_code=upload_data.project_code,
            destination_access_token=token_response.access_token,
            job_id=str(upload_data.job_id),
            session_id=str(upload_data.session_id),
            operator=upload_data.operator,
            access_token=access_token,
        ),
    )
    await queue_service_client.send_message(message.dict())

    await device_storage.delete_upload_data(upload_key)

    return Response(status_code=HTTPStatus.ACCEPTED)
