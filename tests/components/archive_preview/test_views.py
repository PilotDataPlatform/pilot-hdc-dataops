# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from uuid import UUID

from dataops.components.archive_preview.crud import ArchivePreviewCRUD

file_id = 'ca852835-706b-4fb5-898d-6fcbfbf87160'
file_id_invalid = '6fb085f5-1e43-4d34-b3bb-09d6535f27a8'
file_id_db = '689665f9-eb57-4029-9fb4-526ce743d1c9'


class TestArchivePreviewViews:
    async def test_create_preview_return_200(self, test_client, setup_archive_table, db_session):
        archive_preview_crud = ArchivePreviewCRUD(db_session)
        payload = {
            'file_id': file_id,
            'archive_preview': {
                'test.py': {'filename': 'test.py', 'size': 1111, 'is_dir': False},
                'dir2': {'is_dir': True, 'test2.py': {'filename': 'test22.py', 'size': 999, 'is_dir': False}},
            },
        }

        result = await test_client.post('/v1/archive', json=payload)
        res = result.json()
        assert result.status_code == 200
        assert res == payload
        retrived_archive = await archive_preview_crud.retrieve_by_file_id(UUID(file_id))
        assert retrived_archive.file_id == UUID(file_id)

    async def test_create_preview_duplicate_entry_return_409(self, test_client, setup_archive_table):
        payload = {
            'file_id': file_id_db,
            'archive_preview': {'test.py': {'filename': 'test.py', 'size': 1111, 'is_dir': False}},
        }
        result = await test_client.post('/v1/archive', json=payload)
        res = result.json()
        assert result.status_code == 409
        assert res == {'error': {'code': 'global.already_exists', 'details': 'Target resource already exists'}}

    async def test_get_preview_return_200(self, test_client, setup_archive_table):
        payload = {
            'file_id': file_id_db,
        }
        result = await test_client.get('/v1/archive', query_string=payload)
        res = result.json()
        assert result.status_code == 200
        assert res == {
            'file_id': '689665f9-eb57-4029-9fb4-526ce743d1c9',
            'archive_preview': {
                'script.py': {'filename': 'script.py', 'size': 2550, 'is_dir': False},
                'dir2': {'is_dir': True, 'script2.py': {'filename': 'script2.py', 'size': 1219, 'is_dir': False}},
            },
        }

    async def test_get_preview_geid_not_found_return_404(self, test_client, setup_archive_table):
        payload = {
            'file_id': file_id_invalid,
        }
        result = await test_client.get('/v1/archive', query_string=payload)
        res = result.json()
        assert result.status_code == 404
        assert res == {'error': {'code': 'global.not_found', 'details': 'Requested resource is not found'}}

    async def test_delete_preview_return_200(self, test_client, setup_archive_table):
        payload = {
            'file_id': file_id_db,
        }
        result = await test_client.delete('/v1/archive', json=payload)
        assert result.status_code == 204
