"""PySAM connector for the SysML v2 Pilot API server (see sysml-api/)."""

from ansys.sam.sysml2.api.template_sysml2_api_connector import (
    TemplateSysML2APIConnector,
)
from ansys.sam.sysml2.classes.http_request import HttpRequest

DEFAULT_SERVER_URL = "http://localhost:9000"


class PilotSysML2APIConnector(TemplateSysML2APIConnector):
    """Connects PySAM to a standard SysML v2 API server without authentication.

    PySAM only ships a connector for Ansys SAM, which adds an organization path
    and a bearer token. The pilot server exposes the API at its root.
    """

    def __init__(self, server_url: str = DEFAULT_SERVER_URL, use_ssl: bool = False):
        super().__init__(use_ssl)
        self._server_url = server_url.rstrip("/")

    def _build_endpoint(self, endpoint: str) -> str:
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"{self._server_url}{endpoint}"

    def _add_authentication_field(self, http_request: HttpRequest) -> HttpRequest:
        return http_request
