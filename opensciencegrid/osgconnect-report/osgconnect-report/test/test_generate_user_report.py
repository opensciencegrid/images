import pytest

from generate_user_report import get_new_account_requests
from generate_user_report import get_new_accounts_accepted_and_rejected
from generate_user_report import get_new_accounts_accepted_in_training_group
from generate_user_report import get_new_accounts_accepted_in_non_training_group

class TestGetNewAccountRequests: 
    @pytest.mark.parametrize(
        "prev_snapshot, curr_snapshot",
        [
            (
                {   
                    "date": "2021-Jan-01 00:00:01.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "pending",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "pending",
                                "root.osg.training2021": "pending",
                                "root.osg.non_training": "pending"
                            }
                        },
                        "pam_beesly": {
                            "osg_state": "active",
                            "join_date": "2021-Jan-01 04:46:25.868712 UTC",
                            "groups": {
                                "root.osg": "active",
                                "root.osg.non_training": "active"
                            }
                        }
                    }
                },
                {
                "date": "2021-Jan-07 00:00:00.000000 UTC",
                "users": {
                    "jim_halpert": {
                        "osg_state": "active",
                        "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                        "groups": {
                            "root.osg": "active",
                            "root.osg.training2021": "active",
                            "root.osg.non_training": "active"
                        }
                    },
                    "pam_beesly": {
                        "osg_state": "active",
                        "join_date": "2021-Jan-01 04:46:25.868712 UTC",
                        "groups": {
                            "root.osg": "active",
                            "root.osg.non_training": "active",
                            "root.osg.training2021": "pending"
                        }
                    }
                }
            }
            )
        ]
    )   
    def test_get_new_account_requests(self, prev_snapshot, curr_snapshot):
        result = get_new_account_requests(prev_snapshot, curr_snapshot)
        assert result == ["pam_beesly"]

    @pytest.mark.parametrize(
        "prev_snapshot, curr_snapshot, expected",
        [
            (
                {   
                    "date": "2021-Jan-01 00:00:01.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "pending",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "pending",
                                "root.osg.training2021": "pending",
                                "root.osg.non_training": "pending"
                            }
                        },
                        "pam_beesly": {
                            "osg_state": "active",
                            "join_date": "2020-Jan-01 04:46:25.868712 UTC",
                            "groups": {
                                "root.osg": "active",
                                "root.osg.non_training": "active"
                            }
                        }
                    }
                },
                {
                "date": "2021-Jan-07 00:00:00.000000 UTC",
                "users": {
                    "jim_halpert": {
                        "osg_state": "active",
                        "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                        "groups": {
                            "root.osg": "active",
                            "root.osg.training2021": "active",
                            "root.osg.non_training": "active"
                        }
                    },
                    "pam_beesly": {
                        "osg_state": "active",
                        "join_date": "2020-Jan-01 04:46:25.868712 UTC",
                        "groups": {
                            "root.osg": "active",
                            "root.osg.non_training": "active",
                            "root.osg.training2021": "pending"
                        }
                    }
                }
            },
            (["jim_halpert"],[])
            ),
            (
                {   
                    "date": "2021-Jan-01 00:00:01.000000 UTC",
                    "users": dict()
                },
                {
                "date": "2021-Jan-07 00:00:00.000000 UTC",
                "users": {
                    "jim_halpert": {
                        "osg_state": "active",
                        "join_date": "2021-Jan-02 00:00:00.000000 UTC",
                        "groups": {
                            "root.osg": "active",
                            "root.osg.training2021": "active",
                            "root.osg.non_training": "active"
                        }
                    }
                }
            },
            (["jim_halpert"],[])    
            ),
           (
                {   
                    "date": "2021-Jan-01 00:00:01.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "pending",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "pending",
                                "root.osg.training2021": "pending",
                                "root.osg.non_training": "pending"
                            }
                        },
                    }
                },
                {
                "date": "2021-Jan-07 00:00:00.000000 UTC",
                "users": dict()
            },
            ([],["jim_halpert"])
            ),
           (
                {   
                    "date": "2021-Jan-01 00:00:01.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "pending",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "pending",
                                "root.osg.training2021": "pending",
                                "root.osg.non_training": "pending"
                            }
                        },
                    }
                },
                {
                "date": "2021-Jan-07 00:00:00.000000 UTC",
                "users": dict()
            },
            ([],["jim_halpert"])
            ),
           (
                {   
                    "date": "2021-Jan-01 00:00:01.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "pending",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "pending",
                                "root.osg.training2021": "pending",
                                "root.osg.non_training": "pending"
                            }
                        },
                    }
                },
                {
                "date": "2021-Jan-07 00:00:00.000000 UTC",
                "users": {
                    "jim_halpert": {
                        "osg_state": "pending",
                        "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                        "groups": dict()
                    },
                }
            },
            ([],["jim_halpert"])
            ),
        ]
    )
    def test_get_new_accounts_accepted_and_rejected(self, prev_snapshot, curr_snapshot, expected):
        result = get_new_accounts_accepted_and_rejected(prev_snapshot, curr_snapshot)
        assert result == expected
    @pytest.mark.parametrize(
        "curr_snapshot, expected_result",
        [
            (
                {
                    "date": "2021-Jan-07 00:00:00.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "active",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "active",
                                "root.osg.training2021": "active",
                                "root.osg.non_training": "active"
                            }
                        }
                    }
                },
                ["jim_halpert"]
            ),
            (
                {
                    "date": "2021-Jan-07 00:00:00.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "active",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "active",
                                "root.osg.non_training": "active"
                            }
                        }
                    }
                },
                [] 
            )
        ]
    )
    def test_get_new_accounts_accepted_in_training_group(self, curr_snapshot, expected_result):
        result = get_new_accounts_accepted_in_training_group(
            new_acts_accepted=["jim_halpert"],
            curr_snapshot=curr_snapshot,
            training_projects={"root.osg.training2021"}
        )

        assert result == expected_result
    
    @pytest.mark.parametrize(
        "curr_snapshot, exclude, training_groups, expected_result",
        [
            (
                {
                    "date": "2021-Jan-07 00:00:00.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "active",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "active",
                                "root.osg.training2021": "active",
                                "root.osg.non_training": "active"
                            }
                        }
                    }
                },
                {"root", "root.osg"},
                {"root.osg.training2021"},
                ["jim_halpert"]
            ),
            (
                {
                    "date": "2021-Jan-07 00:00:00.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "active",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "active",
                                "root.osg.training2021": "active",
                            }
                        }
                    }
                },
                {"root", "root.osg"},
                {"root.osg.training2021"},
                []
            ),
            (
                {
                    "date": "2021-Jan-07 00:00:00.000000 UTC",
                    "users": {
                        "jim_halpert": {
                            "osg_state": "active",
                            "join_date": "2021-Jan-01 00:00:00.000000 UTC",
                            "groups": {
                                "root.osg": "active",
                                "root.osg.training2021": "active",
                                "root.osg.non_training": "pending"
                            }
                        }
                    }
                },
                {"root", "root.osg"},
                {"root.osg.training2021"},
                ["jim_halpert"]
            )
        ]
    )
    def test_get_new_accepted_in_non_training_group(
            self, 
            curr_snapshot, 
            exclude,
            training_groups,
            expected_result
        ):
        result = get_new_accounts_accepted_in_non_training_group(
            new_acts_accepted=["jim_halpert"],
            curr_snapshot=curr_snapshot,
            training_projects={"root.osg.training2021"},
            exclude=exclude
        )

        assert result == expected_result
