#!/bin/bash
# License Compliance Check Script
# MemoryBank Project - S0-LIC Implementation
# Validates that no GPL licenses are present and reports on all licenses

set -e

echo "🔍 License Compliance Check - MemoryBank Project"
echo "================================================="

# Configuration
REPORTS_DIR="reports/license-compliance"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SCAN_FILE="$REPORTS_DIR/scan_$TIMESTAMP.txt"
JSON_FILE="$REPORTS_DIR/scan_$TIMESTAMP.json"
SUMMARY_FILE="$REPORTS_DIR/compliance_summary_$TIMESTAMP.md"

# Create reports directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

echo "📋 Generating license reports..."

# Generate license reports in multiple formats
pip-licenses --format=plain --output-file="$SCAN_FILE"
pip-licenses --format=json --output-file="$JSON_FILE"

echo "✅ License reports generated:"
echo "   - Text: $SCAN_FILE"
echo "   - JSON: $JSON_FILE"

# Check for critical GPL violations (excluding LGPL)
echo ""
echo "🚨 Checking for CRITICAL GPL violations..."
GPL_VIOLATIONS=$(pip-licenses --format=plain | grep -E "(GNU General Public License|^GPL|AGPL)" | grep -v "LGPL" | wc -l || echo "0")

if [ "$GPL_VIOLATIONS" -gt 0 ]; then
    echo "❌ CRITICAL: GPL license violations found!"
    echo "The following GPL licenses were detected:"
    pip-licenses --format=plain | grep -E "(GNU General Public License|^GPL|AGPL)" | grep -v "LGPL" || echo "None"
    exit 1
else
    echo "✅ SUCCESS: No critical GPL licenses found!"
fi

# Check for LGPL licenses (warning level)
echo ""
echo "⚠️  Checking for LGPL licenses (review required)..."
LGPL_COUNT=$(pip-licenses --format=plain | grep -c "LGPL" || echo "0")

if [ "$LGPL_COUNT" -gt 0 ]; then
    echo "⚠️  WARNING: $LGPL_COUNT LGPL licenses found (review required):"
    pip-licenses --format=plain | grep "LGPL" || echo "None"
else
    echo "✅ No LGPL licenses found"
fi

# Check for unknown licenses
echo ""
echo "❓ Checking for UNKNOWN licenses..."
UNKNOWN_COUNT=$(pip-licenses --format=plain | grep -c "UNKNOWN" || echo "0")

if [ "$UNKNOWN_COUNT" -gt 0 ]; then
    echo "⚠️  WARNING: $UNKNOWN_COUNT packages with UNKNOWN licenses found:"
    pip-licenses --format=plain | grep "UNKNOWN" || echo "None"
else
    echo "✅ No UNKNOWN licenses found"
fi

# Generate summary report
echo ""
echo "📊 Generating compliance summary..."

cat > "$SUMMARY_FILE" << EOF
# License Compliance Summary
**Generated**: $(date)
**Scan ID**: $TIMESTAMP

## 🎯 Compliance Status

### Critical Issues (GPL Licenses)
- **Status**: $([ "$GPL_VIOLATIONS" -eq 0 ] && echo "✅ COMPLIANT" || echo "❌ VIOLATION")
- **Count**: $GPL_VIOLATIONS

### Review Required (LGPL Licenses)  
- **Status**: $([ "$LGPL_COUNT" -eq 0 ] && echo "✅ CLEAR" || echo "⚠️ REVIEW NEEDED")
- **Count**: $LGPL_COUNT

### Unknown Licenses
- **Status**: $([ "$UNKNOWN_COUNT" -eq 0 ] && echo "✅ CLEAR" || echo "⚠️ INVESTIGATION NEEDED")
- **Count**: $UNKNOWN_COUNT

## 📋 License Distribution

EOF

# Add license distribution to summary
echo "### License Types Found:" >> "$SUMMARY_FILE"
pip-licenses --format=plain | awk 'NR>2 {print $3}' | sort | uniq -c | sort -nr | head -20 | while read count license; do
    echo "- **$license**: $count packages" >> "$SUMMARY_FILE"
done

echo "" >> "$SUMMARY_FILE"
echo "## 📁 Files Generated" >> "$SUMMARY_FILE"
echo "- **Full Report**: \`$SCAN_FILE\`" >> "$SUMMARY_FILE"
echo "- **JSON Data**: \`$JSON_FILE\`" >> "$SUMMARY_FILE"
echo "- **Summary**: \`$SUMMARY_FILE\`" >> "$SUMMARY_FILE"

echo "📋 Summary report created: $SUMMARY_FILE"

# Final status
echo ""
echo "🎯 FINAL STATUS:"
if [ "$GPL_VIOLATIONS" -eq 0 ]; then
    echo "✅ LICENSE COMPLIANCE: PASSED"
    echo "   - No critical GPL violations detected"
    echo "   - Project meets license policy requirements"
    exit 0
else
    echo "❌ LICENSE COMPLIANCE: FAILED"
    echo "   - Critical GPL violations must be resolved"
    exit 1
fi 