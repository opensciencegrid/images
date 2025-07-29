<?php

#
# /etc/ganglia/conf.php
#
# You can use this file to override default settings.
#
# For a list of available options, see /usr/share/ganglia/conf_default.php
#

# use chicago tz
$conf['rrdtool'] = "env TZ='America/Chicago' /usr/bin/rrdtool";

#
# Default metric
#
$conf['default_metric'] = "TotalRunningJobs";

# If set to yes, will display stacked graph (aggregated metric across hosts) in cluster view
$conf['show_stacked_graphs'] = 0;

# Are heatmaps enabled
$conf['heatmaps_enabled'] = 0;

# If set to false the grid view under the main tab will be displayed only if
# the grid name is not "unspecified", or a parent grid has been defined.
# If set to true the grid view will always be displayed even when only a
# single cluster has been defined.
$conf['always_display_grid_view'] = false;

# use rrdcached
# disabled as caching did not work with the ce dashboard
#$conf['rrdcached_socket'] = "unix:/tmp/rrdcached.read.sock";

?>
