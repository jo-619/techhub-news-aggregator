#!/bin/bash

# Setup Cron Job for Tech News Scheduler
# This script sets up a cron job to run the tech news collection every hour

echo "⏰ Setting up hourly tech news collection..."

# Get the current directory
CURRENT_DIR=$(pwd)
PYTHON_PATH="$CURRENT_DIR/venv/bin/python"
SCRIPT_PATH="$CURRENT_DIR/tech_scheduler.py"

echo "📁 Current directory: $CURRENT_DIR"
echo "🐍 Python path: $PYTHON_PATH"
echo "📜 Script path: $SCRIPT_PATH"

# Create the cron job entry
CRON_ENTRY="0 * * * * cd $CURRENT_DIR && $PYTHON_PATH $SCRIPT_PATH --once >> $CURRENT_DIR/news_cron.log 2>&1"

echo "📝 Cron job entry:"
echo "$CRON_ENTRY"
echo ""

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo "🕐 Tech news will be collected every hour"
    echo "📋 To view cron jobs: crontab -l"
    echo "🗑️  To remove cron job: crontab -e (then delete the line)"
    echo "📊 Logs will be saved to: $CURRENT_DIR/news_cron.log"
else
    echo "❌ Failed to add cron job"
    echo "💡 Try running: crontab -e"
    echo "   Then add this line:"
    echo "   $CRON_ENTRY"
fi
