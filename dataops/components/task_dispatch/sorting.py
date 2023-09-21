# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

def _get_update_time(x: dict) -> int:
    """Function for getting update timestamp."""
    return x.get('update_timestamp', 0)


def sort_by_update_time(jobs: []) -> list:
    """Function for sorting update timestamp in descending order."""
    jobs.sort(key=_get_update_time, reverse=True)
    return jobs
