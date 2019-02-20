.PHONY: configmap

configmap:
	-kubectl delete configmap cvmfs-osg-config -n cvmfs
	kubectl create configmap cvmfs-osg-config -n cvmfs --from-file=default.local

