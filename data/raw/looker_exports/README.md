# Looker Studio Datasets

This directory contains loan tape data exported from Looker Studio dashboard.

## Dataset Description

The Looker Studio report contains comprehensive loan portfolio analytics:
- **Dashboard URL**: Obtain the production Looker Studio link from the team's secure analytics documentation or access management system (report name: "Loan Portfolio Analytics").

## Files (To be uploaded)

Three primary datasets should be placed in this directory:

### 1. Abaco-Loan-Tape_Loan-Data_Table-6.csv
- **Description**: Core loan tape data including loan amounts, rates, terms, and portfolio metrics
- **Source**: Looker Studio - Loan Data Table
- **Update Frequency**: Daily

### 2. Abaco-Loan-Tape_Customer-Data_Table-6.csv
- **Description**: Customer information and demographics
- **Source**: Looker Studio - Customer Data Table
- **Update Frequency**: Daily

### 3. Abaco-Loan-Tape_Historic-Real-Payment_Table-6.csv
- **Description**: Historical payment records and transaction data
- **Source**: Looker Studio - Historic Payment Table
- **Update Frequency**: Daily

## Usage

These datasets are used by:
- Risk analytics agents for portfolio monitoring
- Customer segmentation for HubSpot integration
- Financial performance tracking
- Predictive modeling for loan outcomes

## Notes

- Files are CSV format exported from Looker Studio
- Data contains production loan portfolio information
- Upload CSV files directly to this directory via GitHub CLI or desktop client
