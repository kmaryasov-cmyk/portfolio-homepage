ZIP upload to CrewAI AMP requires:
- Correct project structure under src/<project_name>/ (see "Prepare for Deployment")
- main.py entry point with run() for Crew projects
- pyproject.toml with [tool.crewai] type="crew"
- uv.lock is REQUIRED for deployment.

Generate uv.lock locally (internet required):
  crewai install
(or: uv lock)

Then zip the project root and upload via Automations -> Deploy from Code -> Upload ZIP.
