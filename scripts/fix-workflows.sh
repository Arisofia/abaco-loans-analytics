#!/bin/bash

set -e

echo "=========================================="
echo "Workflow Validation & Fix Script"
echo "=========================================="

cd "$(dirname "$0")/.."

echo ""
echo "✅ Step 1: Fix Python Environment"
echo "---"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Reinstall yamllint with compatibility fix
echo "Installing yamllint with pathspec compatibility..."
pip install --upgrade yamllint pathspec --quiet 2>/dev/null || true

# Install actionlint if npm available
if command -v npm &> /dev/null; then
    echo "Installing actionlint..."
    npm install -g @actions/actionlint --silent 2>/dev/null || true
fi

echo ""
echo "✅ Step 2: Validate All Workflows"
echo "---"

WORKFLOW_DIR=".github/workflows"
ERROR_COUNT=0
WARN_COUNT=0

# Test yamllint
if command -v yamllint &> /dev/null; then
    echo "Running yamllint on all workflows..."
    if yamllint "$WORKFLOW_DIR" 2>/dev/null | grep -q "error"; then
        echo "⚠️  Some YAML errors found (see below)"
        yamllint "$WORKFLOW_DIR" || WARN_COUNT=$((WARN_COUNT + 1))
    else
        echo "✅ yamllint: All workflows valid"
    fi
else
    echo "⚠️  yamllint not available - installing..."
    pip install yamllint --quiet
fi

# Test actionlint
if command -v actionlint &> /dev/null; then
    echo "Running actionlint on all workflows..."
    if actionlint "$WORKFLOW_DIR"/*.yml 2>&1 | grep -q "error"; then
        echo "⚠️  Some GitHub Actions errors found"
        ERROR_COUNT=$((ERROR_COUNT + 1))
    else
        echo "✅ actionlint: All workflows valid"
    fi
else
    echo "⚠️  actionlint not installed"
fi

# Python validation
echo ""
echo "Running Python YAML validation..."
python3 << 'PYEOF'
import os
import yaml

workflow_dir = ".github/workflows"
errors = 0

for filename in sorted(os.listdir(workflow_dir)):
    if not filename.endswith(('.yml', '.yaml')):
        continue
    
    filepath = os.path.join(workflow_dir, filename)
    try:
        with open(filepath) as f:
            workflow = yaml.safe_load(f)
        
        if not workflow:
            print(f"  ❌ {filename}: Empty workflow")
            errors += 1
            continue
        
        # Basic validation
        if 'name' not in workflow:
            print(f"  ❌ {filename}: Missing 'name'")
            errors += 1
        if 'on' not in workflow or not workflow['on']:
            print(f"  ❌ {filename}: Missing 'on' trigger")
            errors += 1
        if 'jobs' not in workflow or not workflow['jobs']:
            print(f"  ❌ {filename}: Missing 'jobs'")
            errors += 1
        else:
            print(f"  ✅ {filename}: Valid")
            
    except yaml.YAMLError as e:
        print(f"  ❌ {filename}: YAML error - {str(e).split(chr(10))[0]}")
        errors += 1
    except Exception as e:
        print(f"  ❌ {filename}: {str(e)}")
        errors += 1

if errors == 0:
    print("\n✅ All workflows have valid structure")
else:
    print(f"\n❌ Found {errors} workflow issues")
    exit(1)
PYEOF

echo ""
echo "=========================================="
echo "✅ Validation Complete"
echo "=========================================="
