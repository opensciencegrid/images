# Create a frontier pod in the default cvsfm namespace
kubectl create -f frontier.yaml
# Also create a service to make it easy to discover
kubectl create -f service-frontier.yaml

