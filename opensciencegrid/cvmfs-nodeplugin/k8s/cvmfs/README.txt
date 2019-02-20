# Important: Make sure the frontend-squid service has been created

# create configmap in the default cvmfs namespace
make

# create the CVMFS k8s CSI plugin in the default cvmfs namespace
# Note: Relying on gitlab-registry.nautilus.optiputer.net/prp/cvmfs-csi
kubectl create -f csi-processes/

# Create the storageclasses in the default cvmfs namespace
kubectl create -f storageclasses/

# Create the PersistentStorageClaims for both osg and osggpus namespaces
kubectl create -n osg -f pvcs/
kubectl create -n osggpus -f pvcs/
