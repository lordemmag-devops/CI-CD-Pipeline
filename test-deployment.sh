#!/bin/bash

# Test script for deployed application
echo "Testing deployed application..."

# Get external IP
EXTERNAL_IP=$(kubectl get ingress python-app-ingress -n python-ci-cd -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$EXTERNAL_IP" ]; then
    echo "No external IP found. Using port-forward for testing..."
    kubectl port-forward -n python-ci-cd service/python-app 8080:80 &
    PF_PID=$!
    sleep 5
    
    # Test endpoints
    curl -f http://localhost:8080/ || echo "Home endpoint failed"
    curl -f http://localhost:8080/health || echo "Health endpoint failed"
    
    kill $PF_PID
else
    echo "External IP: $EXTERNAL_IP"
    curl -f http://$EXTERNAL_IP/ || echo "Home endpoint failed"
    curl -f http://$EXTERNAL_IP/health || echo "Health endpoint failed"
fi

# Load testing
echo "Running load test..."
for i in {1..10}; do
    curl -s http://localhost:8080/ > /dev/null &
done
wait

echo "Testing complete!"