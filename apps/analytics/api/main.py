from fastapi import FastAPI, HTTPException, BackgroundTasks
import json
from pathlib import Path
from datetime import datetime

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
        raise HTTPException(status_code=500, detail=f"Error reading manifest: {str(e)}")

@app.post("/api/pipeline/trigger")
async def trigger_pipeline(background_tasks: BackgroundTasks, input_file: str = "data/abaco_portfolio_calculations.csv"):
    """Trigger the Prefect pipeline flow as a background task."""
    from python.pipeline.prefect_orchestrator import abaco_pipeline_flow
    
    # In a production env, we'd use prefect's deployment API
    # For this implementation, we run the flow function directly in background
    background_tasks.add_task(abaco_pipeline_flow, input_file=input_file)
    
    return {"message": "Pipeline triggered successfully", "input_file": input_file}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
