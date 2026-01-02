from pathlib import Path
from typing import Any, Dict
from prefect import flow, task, get_run_logger
from python.pipeline.data_ingestion import UnifiedIngestion
from python.pipeline.data_transformation import UnifiedTransformation
from python.pipeline.kpi_calculation import UnifiedCalculationV2
from python.pipeline.output import UnifiedOutput
from python.pipeline.orchestrator import PipelineConfig
from python.pipeline.data_validation_gx import validate_loan_data
from python.agents.tools import send_slack_notification

@task(retries=3, retry_delay_seconds=60)
def ingestion_task(config: Dict[str, Any], input_file: Path):
    logger = get_run_logger()
    logger.info(f"Starting ingestion for {input_file}")
    ingestion = UnifiedIngestion(config)
    # Assume file source for now
    raw_archive_dir = Path(config.get("run", {}).get("raw_archive_dir", "data/raw/cascade"))
    result = ingestion.ingest_file(input_file, archive_dir=raw_archive_dir)
    
    # Integrate Great Expectations
    dq_passed = validate_loan_data(result.df)
    if not dq_passed:
        logger.warning("Great Expectations validation failed!")
        send_slack_notification(
            f"⚠️ *Data Quality Alert*: GX validation failed for {input_file}",
            channel="kpi-compliance"
        )
        
    return result

@task
def transformation_task(config: Dict[str, Any], df: Any, run_id: str):
    logger = get_run_logger()
    logger.info(f"Starting transformation for run {run_id}")
    transformation = UnifiedTransformation(config, run_id=run_id)
    return transformation.transform(df, user="prefect")

@task
def calculation_task(config: Dict[str, Any], df: Any, run_id: str):
    logger = get_run_logger()
    logger.info(f"Starting KPI calculation for run {run_id}")
    calculation = UnifiedCalculationV2(config, run_id=run_id)
    # For now, no baseline metrics passed to simplify
    return calculation.calculate(df, baseline_metrics=None)

@task
def output_task(config: Dict[str, Any], transformation_result: Any, calculation_result: Any, run_id: str):
    logger = get_run_logger()
    logger.info(f"Starting output persistence for run {run_id}")
    output = UnifiedOutput(config, run_id=run_id)
    
    # We can add Supabase persistence here or in UnifiedOutput.persist
    result = output.persist(
        transformation_result.df,
        calculation_result.metrics,
        metadata={
            "transformation": transformation_result.lineage,
            "calculation": calculation_result.audit_trail
        },
        run_ids={"pipeline": run_id}
    )
    return result

@flow(name="Abaco Data Pipeline")
def abaco_pipeline_flow(input_file: str = "data/abaco_portfolio_calculations.csv"):
    config_mgr = PipelineConfig()
    config = config_mgr.config
    input_path = Path(input_file)
    
    ingest_res = ingestion_task(config, input_path)
    run_id = f"prefect_{ingest_res.run_id}"
    
    trans_res = transformation_task(config, ingest_res.df, run_id)
    calc_res = calculation_task(config, trans_res.df, run_id)
    out_res = output_task(config, trans_res, calc_res, run_id)
    
    return out_res

if __name__ == "__main__":
    abaco_pipeline_flow()
