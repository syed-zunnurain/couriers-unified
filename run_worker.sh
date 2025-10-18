#!/bin/bash

# Shipment Request Worker Script
# This script runs the shipment request processing worker

echo "Starting Shipment Request Worker..."
echo "Press Ctrl+C to stop"

# Run the worker in a loop
while true; do
    echo "$(date): Processing shipment requests..."
    
    # Run the worker command
    docker-compose run --rm app sh -c "python manage.py process_shipment_requests --batch-size 20"
    
    # Wait 30 seconds before next run
    echo "$(date): Waiting 30 seconds before next run..."
    sleep 30
done
