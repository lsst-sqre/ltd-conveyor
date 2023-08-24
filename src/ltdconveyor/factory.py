"""Factory for Keeper services and storage adapters."""

from __future__ import annotations

from httpx import AsyncClient

from ltdconveyor.services.projects import ProjectService
from ltdconveyor.storage import keeper


class Factory:
    """LTD Conveyor component factory."""

    def __init__(
        self,
        http_client: AsyncClient,
        api_base: str,
        api_username: str,
        api_password: str,
    ) -> None:
        self.http_client = http_client
        self.api_base = api_base
        self.api_username = api_username
        self.api_password = api_password

    def get_keeper_client(self) -> keeper.KeeperClient:
        return keeper.KeeperClient(
            base_url=self.api_base,
            username=self.api_username,
            password=self.api_password,
            http_client=self.http_client,
        )

    def get_project_service(self) -> ProjectService:
        return ProjectService(
            keeper_client=self.get_keeper_client(),
            http_client=self.http_client,
        )
