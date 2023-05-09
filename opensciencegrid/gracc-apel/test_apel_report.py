"""
Testing the apel_report.py script

"""

import unittest
from io import StringIO
import apel_report


class TestApelReport(unittest.TestCase):
    """
    Test the apel_report.py script
    """

    @staticmethod
    def parse_reports(reports: str) -> list[dict]:
        """
        Parse the reports string into a list of lines.  Example report:

        Site: Nebraska
        SubmitHost: hepspec-hosts
        VO: cms
        EarliestEndTime: 0
        LatestEndTime: 86499
        Month: 05
        Year: 2023
        Infrastructure: Gratia-OSG
        GlobalUserName: cms
        Processors: 1
        NodeCount: 1
        WallDuration: 90
        CpuDuration: 90
        NormalisedWallDuration: 90
        NormalisedCpuDuration: 90
        NumberOfJobs: 0
        %%
        Site: Nebraska
        SubmitHost: hepscore-hosts
        VO: cms
        EarliestEndTime: 0
        LatestEndTime: 86499
        Month: 05
        Year: 2023
        Infrastructure: Gratia-OSG
        GlobalUserName: cms
        Processors: 1
        NodeCount: 1
        WallDuration: 10
        CpuDuration: 10
        NormalisedWallDuration: 10
        NormalisedCpuDuration: 10
        NumberOfJobs: 0
        %%

        """
        # First spit by the separator, %%
        reports = reports.strip().split("%%")
        to_return = []

        # Each line is in the form of <key>:<value>
        # Split each line by the colon and return the value
        for report in reports:
            report_dict = {}
            for line in report.split("\n"):
                if line.strip() == "":
                    continue
                kv = line.split(":")
                try:
                    report_dict[kv[0].strip()] = kv[1].strip()
                except IndexError as ie:
                    print("Failure on line:", line)
                    raise
            to_return.append(report_dict)
        
        return to_return

    def test_print_rk_recr(self):
        """
        Test the print_rk_recr function
        """
        # First create the data structures we need
        class rk:
            site = "Nebraska"
            vo = "cms"
            cores = 1
            dn = "cms"
        
        class rec:
            mintime = 0
            maxtime = 100
            walldur = 100
            cpudur = 100
            nf = 1
            njobs = 1

        # Create a textio object to capture the output
        # We need to use StringIO because print_rk_recr uses print
        # and we want to capture the output
        to_write = StringIO()

        # Now call the function
        apel_report.print_rk_recr(2023, 5, rk, rec, to_write)

        # Now check the output
        reports = self.parse_reports(to_write.getvalue())

        self.assertEqual("Nebraska", reports[0]['Site'])
        self.assertEqual("hepspec-hosts", reports[0]['SubmitHost'])
        self.assertEqual("hepscore-hosts", reports[1]['SubmitHost'])



if __name__ == '__main__':
    unittest.main()

