# Important: Make sure the frontend-squid service has been created

# check what the Squid IP is and adjust daemonset/cvmfs-nodeplugin.yaml
./show_squid.sh

# the daemonset will need service account
kubectl create -f  accounts/

# create the cmvmfs supporting processes in default cvmfs namespace
kubectl create -f pv-root/
kubectl create -f daemonset/

# Create the PersistentStorageClaims for both osggpus and osgcpus namespaces
kubectl create -f pv-osggpus/
kubectl create -f pv-osgcpus/
