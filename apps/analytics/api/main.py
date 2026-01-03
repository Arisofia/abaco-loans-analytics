import json
from pathlib import Path
from datetime import datetime
import sys

# Ensure the repository root is on sys.path when the app is started as a script
# (when running `python apps/analytics/api/main.py`, sys.path[0] is the script dir).
# This allows imports like `src.pipeline.*` to resolve correctly.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from fastapi import FastAPI, HTTPException, BackgroundTasks

app = FastAPI(title="ABACO Analytics API")

ARTIFACTS_DIR = Path("logs/runs")

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/kpis/latest")
def get_latest_kpis():
    """Fetch the latest KPI results from the most recent run manifest."""
    if not ARTIFACTS_DIR.exists():
        raise HTTPException(status_code=404, detail="No run artifacts found")
        
    # Find the latest manifest
    manifests = sorted(
        ARTIFACTS_DIR.glob("*/**/*_manifest.json"), 
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not manifests:
        raise HTTPException(status_code=404, detail="No manifests found")
        
    latest_manifest_path = manifests[0]
    try:
        with open(latest_manifest_path, "r") as f:
            manifest = json.load(f)
        return {
            "run_id": manifest.get("run_id"),
            "generated_at": manifest.get("generated_at"),
            "metrics": manifest.get("metrics"),
            "quality_checks": manifest.get("quality_checks")
        }
    except Exception as e:
        # Re-raise with chaining so the original exception is preserved
        raise HTTPException(status_code=500, detail=f"Error reading manifest: {str(e)}") from e

@app.post("/api/pipeline/trigger")
async def trigger_pipeline(background_tasks: BackgroundTasks, input_file: str = "data/abaco_portfolio_calculations.csv"):
    """Trigger the Prefect pipeline flow as a background task.

    Execution strategy is configurable via `PIPELINE_EXECUTION_MODE` env var:
      - "inline": import and run the flow object in the web process (not
        recommended for production; useful for local debugging).
      - "subprocess": spawn a separate Python process that runs the flow as a
        detached child (recommended; avoids initializing Prefect in the web
        server process).

    The subprocess approach avoids heavy Prefect/server initialization in the
    API process which can cause runtime import/init issues and block request
    handling.
    """
    import logging
    import os
    import subprocess
    import shlex
    import sys

    logger = logging.getLogger(__name__)

    mode = os.getenv("PIPELINE_EXECUTION_MODE", "subprocess")

    if mode == "inline":
        # Local/debug mode: run the flow object directly (keeps previous behavior)
        from src.pipeline.prefect_orchestrator import abaco_pipeline_flow

        # Run in background via FastAPI BackgroundTasks; exceptions will propagate
        # to the background runner but won't block request handling.
        background_tasks.add_task(abaco_pipeline_flow, input_file=input_file)
        logger.info("Triggered pipeline inline for input: %s", input_file)
        return {"message": "Pipeline triggered (inline)", "input_file": input_file}

    # Default: spawn a detached subprocess to run the flow so the web process is
    # not affected by Prefect initialization, long-running tasks, or heavy deps.
    try:
        python = sys.executable or "python"
        # Build a small python one-liner that reads the input_file from argv[1].
        # Passing the input as an argv value avoids producing Python source with
        # embedded quotes that can break for inputs with special characters.
        script = (
            "import sys; "
            "from src.pipeline.prefect_orchestrator import abaco_pipeline_flow; "
            "abaco_pipeline_flow(input_file=sys.argv[1])"
        )

        # Ensure log dir exists and run subprocess with output redirected so
        # failures are recorded for later investigation.
        log_path = Path("logs/pipeline_subprocess.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            log_file = open(log_path, "a")
        except Exception:
            log_file = subprocess.DEVNULL

        # Start a detached process without shell=True for safety and pass args
        # directly to avoid shell interpretation issues. Use start_new_session to
        # properly detach on Unix-like systems.
        subprocess.Popen(
            [python, "-c", script, input_file],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
        logger.info("Spawned pipeline subprocess for input: %s (logs: %s)", input_file, log_path)
        return {"message": "Pipeline triggered (subprocess)", "input_file": input_file}
    except Exception as e:
        logger.exception("Failed to trigger pipeline: %s", e)
        raise HTTPException(status_code=500, detail="Failed to start pipeline") from e

if __name__ == "__main__":
    import os
    import uvicorn

    host = os.getenv("UVICORN_HOST", "127.0.0.1")
    port = int(os.getenv("UVICORN_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
