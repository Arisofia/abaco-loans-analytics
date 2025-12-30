
from typing import Dict
import logging
import os
from datetime import datetime
import azure.functions as func
from agents.hubspot.segment_manager import SegmentManagerAgent
from agents.base_agent import AgentConfig, AgentContext


"""
Azure Function App for HubSpot Segment Manager Agent.

This function runs on a schedule to create daily HubSpot segments for contacts
created today (Fecha de creación = Hoy).
"""

app = func.FunctionApp()


def _initialize_and_run_agent(trigger_type: str, user_id: str,
                              name_suffix: str) -> Dict:
    """
    Initializes the SegmentManagerAgent, executes the tool, and returns
    the result. This helper function centralizes agent logic to avoid code
    duplication.
    """
    model_name = os.getenv("AGENT_MODEL", "gpt-4")
    temperature = float(os.getenv("AGENT_TEMPERATURE", "0.3"))
    config = AgentConfig(
        name="HubSpotSegmentManager",
        description="Creates daily contact segments in HubSpot",
        model=model_name,
        temperature=temperature
    )
    context = AgentContext(
        user_id=user_id,
        session_id="{}-{}".format(
            trigger_type, datetime.utcnow().strftime('%Y%m%d%H%M%S')
        ),
        metadata={"trigger": trigger_type}
    )
    agent = SegmentManagerAgent(config=config, context=context)
    logging.info(
        "Executing tool 'create_today_segment' with suffix: '%s'",
        name_suffix
    )
    return agent.execute_tool(
        tool_name="create_today_segment",
        tool_input={"name_suffix": name_suffix}
    )


@app.schedule(
    schedule="0 0 8 * * *",
    arg_name="timer",
    run_on_startup=False
)
def hubspot_daily_segment(timer: func.TimerRequest) -> None:
    """Timer-triggered function for daily HubSpot segment creation."""
    timestamp = datetime.utcnow().isoformat()
    if timer.past_due:
        logging.warning(
            'Timer trigger is running late. Timestamp: %s', timestamp
        )
    logging.info(
        'Starting HubSpot daily segment creation at %s', timestamp
    )
    try:
        result = _initialize_and_run_agent(
            trigger_type="timer",
            user_id="system",
            name_suffix="Auto"
        )
        if result.get("success"):
            logging.info(
                "✅ Successfully created segment: %s (ID: %s)",
                result.get('name'), result.get('list_id')
            )
            logging.info("   URL: %s", result.get('url'))
        else:
            error_msg = result.get(
                "error", "Unknown error during segment creation."
            )
            logging.error(
                "❌ Failed to create segment: %s", error_msg
            )
            raise RuntimeError(
                "Segment creation failed: {}".format(error_msg)
            )
    except Exception as e:
        logging.exception(
            "❌ An unhandled error occurred in hubspot_daily_segment: %s", e
        )
        raise
    logging.info(
        "Completed HubSpot daily segment creation at %s",
        datetime.utcnow().isoformat()
    )


@app.route(
    route="create-segment",
    methods=["POST"],
    auth_level=func.AuthLevel.FUNCTION
)
def http_trigger_manual_segment(
    req: func.HttpRequest
) -> func.HttpResponse:
    """HTTP-triggered function for manual segment creation."""
    logging.info('HTTP trigger: Manual HubSpot segment creation requested.')
    try:
        req_body = req.get_json() if req.get_body() else {}
        name_suffix = req_body.get('name_suffix', 'Manual')
    except ValueError:
        name_suffix = 'Manual'
    try:
        result = _initialize_and_run_agent(
            trigger_type="http",
            user_id="http-trigger",
            name_suffix=name_suffix
        )
        if result.get("success"):
            return func.HttpResponse(
                body="Successfully created segment: {}\nURL: {}".format(
                    result.get('name'), result.get('url')
                ),
                status_code=200,
                mimetype="text/plain"
            )
        else:
            return func.HttpResponse(
                body="Failed to create segment: {}".format(
                    result.get('error')
                ),
                status_code=500,
                mimetype="text/plain"
            )
    except Exception as e:
        logging.exception(
            "An unhandled error occurred in manual_segment_creation: %s", e
        )
        return func.HttpResponse(
            body="Internal Server Error: {}".format(str(e)),
            status_code=500,
            mimetype="text/plain"
        )
