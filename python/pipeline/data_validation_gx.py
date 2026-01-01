import great_expectations as gx
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_loan_data(df: pd.DataFrame) -> bool:
    """Validate a DataFrame using the Great Expectations loan_tape_ingestion suite."""
    try:
        context = gx.get_context()
        
        # Create a batch request
        datasource_name = "pandas_datasource"
        if datasource_name not in context.datasources:
            context.add_pandas(name=datasource_name)
            
        validator = context.get_validator(
            batch_request=context.get_datasource(datasource_name).get_batch_request_from_dataframe(
                df, name="loan_tape_batch"
            ),
            expectation_suite_name="loan_tape_ingestion"
        )
        
        results = validator.validate()
        
        if not results["success"]:
            logger.warning("Data quality validation failed.")
            for res in results["results"]:
                if not res["success"]:
                    logger.error(f"Failed expectation: {res['expectation_config']['expectation_type']} on {res['expectation_config']['kwargs'].get('column')}")
            return False
            
        logger.info("Data quality validation passed.")
        return True
        
    except Exception as e:
        logger.error(f"Error during GX validation: {e}")
        return False

if __name__ == "__main__":
    # Simple test
    test_df = pd.DataFrame({
        "loan_id": [1, 2],
        "customer_id": [101, 102],
        "disbursement_date": ["2024-01-01", "2024-01-02"],
        "disbursement_amount": [1000, 2000],
        "interest_rate_apr": [0.25, 0.30],
        "outstanding_loan_value": [1000, 2000]
    })
    success = validate_loan_data(test_df)
    print(f"Validation success: {success}")
