# ada

Ada is a development environment for carrying out system design and verification using SysMLv2 based tooling.

## Setup

The development environment runs in a dev container. This configures a container which installs all the features the IDE needs for writing SysMLv2 models along with the features required for carrying out validation of the models.

Validation scripts read model properties using [Ansys PySAM SysML2](https://sysml2.docs.pyansys.com/) (`ansys-sam-sysml2`), which loads models from a server implementing the standard SysML v2 API. Scripts are managed with the UV package manager (`uv sync`, `uv run`).

## Running the SysML v2 API server

The dev container includes Docker (docker-in-docker), used to run the [SysML v2 Pilot API server](https://github.com/Systems-Modeling/SysML-v2-API-Services) with a PostgreSQL database. From a terminal inside the dev container:

```sh
docker compose -f sysml-api/compose.yaml up -d --build
```

The first build compiles the server from source and takes several minutes. Once running:

- API: `http://localhost:9000` (e.g. `curl localhost:9000/projects`)
- Swagger UI: `http://localhost:9000/docs/` (port 9000 is forwarded to the host)

Other useful commands:

```sh
docker compose -f sysml-api/compose.yaml logs -f api   # follow server logs
docker compose -f sysml-api/compose.yaml down          # stop, keeping data
docker compose -f sysml-api/compose.yaml down -v       # stop and delete all model data
```

To move to a newer pilot release, change `SYSML_RELEASE` in [sysml-api/compose.yaml](sysml-api/compose.yaml) to a tag from the [releases](https://github.com/Systems-Modeling/SysML-v2-API-Services/tags) and rebuild.

### Connecting from PySAM

PySAM only ships a connector for Ansys SAM, so use `ada.pilot_connector.PilotSysML2APIConnector` for the pilot server:

```python
from ansys.sam.sysml2 import SysML2ProjectManager
from ada.pilot_connector import PilotSysML2APIConnector

project_manager = SysML2ProjectManager(PilotSysML2APIConnector("http://localhost:9000"))
for p in project_manager.get_projects():
    print(p["name"], p["@id"])
```

## Resources

[PySAM SysML2 Docs](https://sysml2.docs.pyansys.com/)

[SysML-v2-Pilot-Implementation](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation)
