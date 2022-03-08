import os
os.environ['_CONDOR_GSI_SKIP_HOST_CHECK'] = "true"

from .status import get_pool_status
from .slots import get_pool_slots, get_pool_glidein_slots
from .priorities import get_pool_priorities
from .jobs import Jobs

# disable debug logging, causes memory leak in long-running processes
import htcondor
htcondor.param['TOOL_LOG'] = '/dev/null'
htcondor.enable_log()
