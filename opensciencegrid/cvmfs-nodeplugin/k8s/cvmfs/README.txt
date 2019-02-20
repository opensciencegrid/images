# Create the storageclasses in the default cvmfs namespace
kubectl create -f storageclasses/

# Create the PersistentStorageClaims for both osg and osggpus namespaces
kubectl create -n osg -f pvcs/
kubectl create -n osggpus -f pvcs/
