.PHONY: configmap

configmap:
	-kubectl delete configmap cvmfs-osg-config -n cvmfs
	./create_local.sh && kubectl create configmap cvmfs-osg-config -n cvmfs --from-file=default.local

