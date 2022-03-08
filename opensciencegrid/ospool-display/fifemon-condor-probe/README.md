Fifemon
=======

Collect HTCondor statistics and report into time-series database. All modules
support Graphite, and there is some support for InfluxDB.

Note: this is a fork of the scripts used for monitoring the HTCondor pools
at Fermilab, and while generally intended to be "generic" for any pool still
may require some tweaking to work well for your pool.

Copyright Fermi National Accelerator Laboratory (FNAL/Fermilab). See LICENSE.txt.

Requirements
------------

* Python 2.7 or greater recommended.
* HTCondor libraries and Python bindings
    * https://research.cs.wisc.edu/htcondor/downloads/
	* https://pypi.org/project/htcondor/ (setup.py will install this, see below)
* A running Graphite server (available in EPEL or via PIP)
    * http://graphite.readthedocs.org/en/latest/

Installation
------------

Global install:

    python setup.py install

Installing in a virtualenv:

    virtualenv --system-site-packages .venv
    source .venv/bin/activate
    python setup.py install

Docker:

    docker build -t fifemon .

Running
-------

    fifemon [options] config_file

The setup script will install an executable script named `fifemon`. It
requires a configuration file passed as an argument (see below or
included `fifemon.cfg`). Some runtime options are supported on the
command line, run `fifemon --help` for info.

Running with Docker
-------------------

	docker run fifemon

By default the included `fifemon.cfg` configuration will be used, but
you can easily bind-mount in another:

    docker run -v myconfig.cfg:/fifemon/fifemon.cfg fifemon


Configuration
-------------

Example probe config is in `fifemon.cfg`. A note on constraints:
constraints can either be a boolean, where `true` means no constraint,
a string to be passed directly to HTCondor, or a function, which will
be called at runtime with an `htcondor.Collector` argument and should
return a string constraint. See `constraint_example.py` for an example
of how this could be used.

	[probe]
	# how often to send data in seconds
	interval = 240
	# how many times to retry condor queries
	retries = 2
	# seconds to wait beteeen retries
	delay = 10
	# if true, data is output to stdout and not sent downstream
	test = false
	# run one time and exit, i.e. for running wtih cron
	once = false
	# enable promethus metrics server for monitoring the probe
	publish_metrics = false

	[graphite]
	# enable output to graphite
	enable = true
	# graphite host
	host = localhost
	# graphite pickle port
	port = 2004
	# base namespace for metrics
	namespace = test.condor
	# namespace for probe monitoring metrics
	meta_namespace = test.probes.condor

	[influxdb]
	# enable output to influxdb (not fully supported)
	enable = false
	# influxdb host
	host = localhost
	# influxdb api port
	port = 8086
	# influxdb database
	db = test
	# extra tags to include with all metrics (comma-separated key:value)
	tags = cluster:test

	[condor]
	# central manager/collector host
	pool = localhost
	# collect basic daemon (collector, negotiator, schedd) metrics?
	post_pool_status = true
	# collect machine/startd metrics?
	post_pool_slots = true
	# constraint to limit which startds metrics are collected for
	slot_constraint = true
	# collect glidein-specific startd metrics?
	post_pool_glideins = false
	# collect priorities and quotas?
	post_pool_prio = false
	# constraint to limit which negotiators are queried
	negotiator_constraint = true
	# If true, first try to get priorities and quotas from Accounting classads in collector,
	# then fallback to negotiator. Opposite order if false.
	prefer_accounting = false
	# collect job metrics?
	post_pool_jobs = false
	# constraint to limit which schedds are queried
	schedd_constraint = true
	# Enable GSI (x509 certificate) authorization
	use_gsi_auth = false
	X509_USER_KEY = ""
	X509_USER_CERT = ""
