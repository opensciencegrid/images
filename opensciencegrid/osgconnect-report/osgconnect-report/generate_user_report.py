#!/usr/bin/env python3
import json
import logging
import sys
import smtplib
import argparse
import requests

from collections import defaultdict
from datetime import datetime
from datetime import timezone
from enum import Enum
from pathlib import Path
from typing import List, Set, Union, Tuple

from client import UserApiClient

from tqdm import tqdm

DATE_FMT = "%Y-%b-%d %H:%M:%S.%f %Z"

log = logging.getLogger("reporter")

class GroupMemberState(Enum):
    """Possible group membership states"""
    NONMEMBER = "nonmember"
    PENDING = "pending"
    ACTIVE = "active"
    ADMIN = "admin"
    DISABLED = "disabled"

def get_snapshot(save=True) -> dict:
    """
    Dump a snapshot of the data base into ./snapshots/YYYYMMDD_snapshot.json

    The snapshot contains only information needed to the following for a given
    time period:
    - new account requests
    - new account requests that have already been added to a training project
    - new account requests that have already been added to a non-training project
    - new accounts accepted
    - new accounts accepted and have been added to a training project
    - new accounts accepted and have been added to a non-training project

    The snapshot is formatted as follows:
    {
        "date": "YYYY-Mon-DD HH:MM:SS.MS UTC",
        "users": {
            "<user_name>": {
                "osg_state": "<active | pending | ...>",
                "joing_date": "YYYY-Mon-DD HH:MM:SS.MS UTC",
                "groups": {
                    "<group_name>": "<active | pending | ...>",
                    ...
                } 
            }, ...
        }
    }

    :param save: whether or not to save snapshot to disk, defaults to True
    :type save: bool
    :return: snapshot just written
    :rtype: dict
    """
    TOP_DIR = Path(__file__).parent.resolve()
    client = UserApiClient(TOP_DIR / "osgconnect.token")
    
    snapshot = defaultdict(dict)

    # get the state of all users in the root.osg group
    osg_states = client.get_group_members("root.osg")
    for s in osg_states:
        snapshot[s["user_name"]]["osg_state"] = s["state"]

    # get the join date of all users (it is expected that all users belong to root.osg)
    users = client.get_users()
    for u in users:
        if u["kind"].lower() == "user" and u["metadata"]["unix_name"] in snapshot:
            u = u["metadata"]
            snapshot[u["unix_name"]]["join_date"] = u["join_date"]

    # get the membership information from each group (len(groups) number of api requests...)
    groups = client.get_group_list()
    for group_name in tqdm(groups):
        # only concerned with groups that are part of "root.osg"
        if "root.osg" in group_name:
            memberships = client.get_group_members(group_name)
            for m in memberships:
                if "groups" not in snapshot[m["user_name"]]:
                    snapshot[m["user_name"]]["groups"] = dict()

                snapshot[m["user_name"]]["groups"][group_name] = m["state"]

    log.info("collected {num} users in the root.osg group".format(num=len(snapshot)))

    # add date snapshot was recorded 
    snapshot = {
        "date": datetime.now(timezone.utc).strftime(DATE_FMT),
        "users": snapshot
    }

    # setup directory for snapshot files
    snapshot_dir = TOP_DIR / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)

    snapshot_file = "{date}_snapshot.json".format(date=datetime.now().strftime("%Y%m%d"))
    snapshot_file = snapshot_dir / snapshot_file

    with snapshot_file.open("w") as f:
        json.dump(snapshot, f, indent=1)

    log.info("snapshot written to {file}".format(file=snapshot_file))

    return snapshot

def get_latest_snapshot_on_disk() -> Union[Path, None]:
    """
    Returns the a path object to the latest snapshot file in ./snapshots.

    :return: path to the latest snapshot file or None if none is found
    :rtype: Union[Path, None]
    """
    SNAPSHOT_DIR = Path(__file__).parent.resolve() / "snapshots"

    latest_snapshot_file = None
    latest_snapshot_date = datetime.min

    if SNAPSHOT_DIR.is_dir():
        for f in SNAPSHOT_DIR.iterdir():
            if f.name.endswith("_snapshot.json"):
                with f.open("r") as curr_snapshot_file:
                    curr_snapshot_date = json.load(curr_snapshot_file)["date"]
                    curr_snapshot_date = datetime.strptime(curr_snapshot_date, DATE_FMT)

                    if curr_snapshot_date > latest_snapshot_date:
                        latest_snapshot_date = curr_snapshot_date
                        latest_snapshot_file = f

    return latest_snapshot_file

def get_snapshot_on_disk(snapshot: str) -> dict:
    """Returns the given snapshot as a dict.

    :param snapshot: name of the snapshot
    :type snapshot: str
    :return: dict representation of the snapshot
    :rtype: dict
    :raises FileNotFoundError: given snapshot could not be found 
    """
    SNAPSHOT_DIR = Path(__file__).parent.resolve() / "snapshots"

    target_snapshot = SNAPSHOT_DIR / snapshot

    with target_snapshot.open("r") as f:
        return json.load(f)


def send_report(recipients: List[str], msg_content: str) -> None:

    # TODO: parametrize email recipients.. (or load from file to keep from versioning)
    # TODO: needs exception/error handling

    # get email credentials
    EMAIL_CREDENTIALS = Path(__file__).parent.resolve() / "mailgun.token"
    with EMAIL_CREDENTIALS.open("r") as f:
        token = f.read().strip()

    response = requests.post(
        "https://api.mailgun.net/v3/api.ci-connect.net/messages",
        auth=("api", token),
        data={"from": "OSGConnect Report <mailgun@api.ci-connect.net>",
              "to": recipients,
              "subject": "OSG Connect User Account Reporting",
              "html": msg_content})
    log.info(response.text)


def get_training_groups() -> Set[str]:
    """
    Returns the list of training groups in ./training_groups.json as a set.

    :return: training groups
    :rtype: Set[str]
    """
    try:
        training_groups_file = Path(__file__).parent.resolve() / "training_groups.json"
        with training_groups_file.open("r") as f:
            training_groups = set(json.load(f))

        log.info("found training groups: {tg} in {p}".format(
            tg=training_groups,
            p=training_groups_file
        ))

        return training_groups

    except FileNotFoundError:
        log.error("Unable to find {p}, no training groups set".format(
            p=training_groups_file
        ))
        raise
    except json.JSONDecodeError:
        log.error("Unable to decode {p}, possible formatting error".format(p=training_groups_file))
        raise
    


### New Account Request Reporting ##############################################
def get_new_account_requests(prev_snapshot: dict, curr_snapshot: dict) -> List[str]:
    """
    Gets all new accounts requests that came in during
    prev_snapshot["date"] < user_join_date <= curr_snapshot["date"]. 

    :param prev_snapshot: snapshot previously recorded
    :type prev_snapshot: dict
    :param curr_snapshot: snapshot just recorded
    :type curr_snapshot: dict
    :return: list of users who had requested accounts since the last snapshot was taken
    :rtype: list
    """
    start_date = datetime.strptime(prev_snapshot["date"], DATE_FMT)
    end_date = datetime.strptime(curr_snapshot["date"], DATE_FMT)

    accounts = list()
    for u_name, u_info in curr_snapshot["users"].items():
        # join_date is not present for some users (for example onces that are
        # part of groups other than root.osg)
        if "join_date" in u_info:
            join_date = datetime.strptime(u_info["join_date"], DATE_FMT)

            if start_date < join_date and join_date <= end_date:
                accounts.append(u_name)
    
    log.info("found {n} new account requests from {start} to {end}: {acts}".format(
        n=len(accounts),
        start=start_date,
        end=end_date,
        acts=accounts
    ))

    return accounts

### New Accounts Accepted Reporting ############################################
def get_new_accounts_accepted_and_rejected(prev_snapshot: dict, curr_snapshot: dict) -> Tuple[List[str], List[str]]:
    """
    Gets all accounts that have been accepted and rejected since the last snapshot.  
    An "accepted account" is defined as having its state moved from "pending" to "active".
    A "rejected account" is defined as having been a member of "root.osg" in the
    previous snapshot, but not the current snapshot. 

    :param prev_snapshot: snapshot previously recorded
    :type prev_snapshot: dict
    :param curr_snapshot: snapshot just recorded
    :type curr_snapshot: dict
    :return: lists of users whos accounts have been accepted and rejected
    :rtype: Tuple[List[str], List[str]]
    """
    start_date = datetime.strptime(prev_snapshot["date"], DATE_FMT)
    end_date = datetime.strptime(curr_snapshot["date"], DATE_FMT)

    # accounts[0] is ACCEPTED accounts
    # accounts[1] is REJECTED accounts
    accounts = (list(), list())

    # look at "root.osg" state changes from previous snapshot to current snapshot
    log.debug("looking at root.osg state changes from previous to current snapshot")
    for u_name, u_info in prev_snapshot["users"].items():
        log.debug("working on {}".format(u_name))
        # TODO: figure out what it means to be in group root.osg
        # not all memebers are part of "root.osg", skip those that are not 
        try:
            # only care about members in "root.osg" in previous snapshot
            if "root.osg" in u_info["groups"]:

                # account is accepted iff root.osg state moved from pending -> active from prev to curr snapshot
                if u_info["groups"]["root.osg"] == GroupMemberState.PENDING.value \
                    and curr_snapshot["users"][u_name]["groups"]["root.osg"] == GroupMemberState.ACTIVE.value:

                    # account was accepted!
                    accounts[0].append(u_name)

        # key error accessing curr_snapshot means account from prev not in curr, thus account was rejected
        except KeyError as e:
            # user from prev snapshot not in 
            log.warning("problem key: {}, exception: {}; adding as rejected account".format(u_name, e))
            
            # account was rejected!
            accounts[1].append(u_name)

    # look for accounts have been just requested and accepted between the previous snapshot and the
    # current snapshot (their entries will only exist in the current snapshot and their join
    # date will be after the date of the previous snapshot)
    log.debug("looking at accounts that have been just requested and accepted between snapshots")
    for name, info in curr_snapshot["users"].items():
        log.debug("working on {}".format(name))
        log.debug(info)
        if "root.osg" in info["groups"] \
            and info["groups"]["root.osg"] == GroupMemberState.ACTIVE.value \
            and datetime.strptime(info["join_date"], DATE_FMT) > start_date:

            # account was just accepted!
            accounts[0].append(name)    
    
    log.info(
            "found {n} new accounts that have been accepted from {start} to {end}: {acts}".format(
            n=len(accounts[0]),
            start=start_date,
            end=end_date,
            acts=accounts[0]
        )
    )

    log.info(
        "found {n} new accounts that have been REJECTED from {start} to {end}: {acts}".format(
            n=len(accounts[1]),
            start=start_date,
            end=end_date,
            acts=accounts[1]
        )
    )

    return accounts

def get_new_accounts_accepted_in_training_group(
        new_acts_accepted: List[str], 
        curr_snapshot: dict, 
        training_projects: Set[str]
    ) -> List[str]:
    """
    Gets all accounts that have been accepted and added to a training project.
    "Added to a training group" is defined as showing up as a member in a training
    group with state=<active | pending>.

    :param new_acts_accepted: new accounts accepted since the last snapshot was taken
    :type new_acts_accepted: List[str]
    :param curr_snapshot: snapshot just recorded
    :type curr_snapshot: dict
    :param training_projects: predefined set of training projects to search for
    :type training_projects: Set[str]
    :return: list of users whos accounts have been accepted and added to a training project
    :rtype: List[str]
    """

    accounts = list()

    for user in new_acts_accepted:
        user_groups = curr_snapshot["users"][user]["groups"]

        for group_name, state in user_groups.items():
            if group_name in training_projects and\
                state in {GroupMemberState.ACTIVE.value, GroupMemberState.PENDING.value}:

                accounts.append(user)
                break

    log.info(
            "found {n} accounts that have been accepted and added to a training project: {acts}".format(
            n=len(accounts),
            acts=accounts
        )
    )

    return accounts

def get_new_accounts_accepted_in_non_training_group(
        new_acts_accepted: List[str],
        curr_snapshot: dict, 
        training_projects: Set[str], 
        exclude: Set[str] = {"root", "root.osg", "root.osg.login-nodes", "root.osg.login-nodes.login05", "root.osg.login-nodes.login04"}
    ) -> List[str]:
    """
    Gets all accounts that have been accepted since the last snapshot and have
    been already added to a non training group. "Added to a non training group" is
    defined as showing up as a member in a group that is neither in any of the 
    groups in "exclude" and "training_projects" and having a group state=<active | pending>.

    :param new_acts_accepted: new accounts accepted since the last snapshot was taken
    :type new_acts_accepted: List[str]
    :param curr_snapshot: snapshot just recorded
    :type curr_snapshot: dict
    :param training_projects: predefiend set of training projects to exclude
    :type training_projects: Set[str]
    :param exclude: non-training projects to exclude, defaults to {"root", "root.osg", "root.osg.login-nodes", "root.osg.login-nodes.login05", "root.osg.login-nodes.login04"}
    :type exclude: Set[str], optional
    :return: list of users whos accounts have been accepted and added to a non training project
    :rtype: List[str]
    """
    exclude.update(training_projects)
    accounts = list()

    for user in new_acts_accepted:
        user_groups = curr_snapshot["users"][user]["groups"]

        for group_name, state in user_groups.items():
            if group_name not in exclude and\
                state in {GroupMemberState.ACTIVE.value, GroupMemberState.PENDING.value}:

                accounts.append(user)
                break
    
    log.info(
            "found {n} new accounts accepted that have already been added to a non training project (excluding {excluded}): {acts}".format(
            n=len(accounts),
            excluded=exclude,
            acts=accounts
        )
    )

    return accounts

def parse_args(args=sys.argv[1:]):
    """Argument parsing"""
    parser = argparse.ArgumentParser(
        description="""
        Collects user account metrics, generates an html report, and
        sends it to the given recipients.
        """
    )
    parser.add_argument(
        "--recipients",
        nargs="+",
        help="recipients to which the report will be sent"
    )

    parser.add_argument(
        "--start",
        type=str, 
        help="snapshot to start from, used to 'replay' from a specific snapshot"
    )

    parser.add_argument(
        "--end",
        type=str,
        help="snapshot to end with, used to 'replay' from a specific snapshot"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="enable debug mode"
    )

    return parser.parse_args(args)

if __name__=="__main__":
    args = parse_args()

    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    
    logging.basicConfig(level=log_level)

    # TODO: cleanup smtp code; add error checking; logging

    if args.start:
        previous_snapshot = get_snapshot_on_disk(args.start)
        log.info("using start snapshot: {}".format(args.start))
    else:
        previous_snapshot_file = get_latest_snapshot_on_disk()

        if not previous_snapshot_file:
            log.info("No previous snapshot found, exiting")
            sys.exit(1)

        with previous_snapshot_file.open("r") as f:
            previous_snapshot = json.load(f)
    
    if args.end:
        current_snapshot = get_snapshot_on_disk(args.end)
        log.info("using end snapshot: {}".format(args.end))
    else:
        get_snapshot(save=True)
        with get_latest_snapshot_on_disk().open("r") as f:
            current_snapshot = json.load(f)
    
    previous_snapshot_date = datetime.strptime(previous_snapshot["date"], DATE_FMT)
    current_snapshot_date = datetime.strptime(current_snapshot["date"], DATE_FMT)
    report_duration_in_days = (current_snapshot_date - previous_snapshot_date).days
    
    training_groups = get_training_groups()

    # new account requests
    new_account_requests = get_new_account_requests(
            prev_snapshot=previous_snapshot,
            curr_snapshot=current_snapshot
        )

    # accounts accepted
    new_accounts_accepted_and_rejected = get_new_accounts_accepted_and_rejected(
        prev_snapshot=previous_snapshot,
        curr_snapshot=current_snapshot
    )

    new_accounts_accepted = new_accounts_accepted_and_rejected[0]
    new_accounts_rejected = new_accounts_accepted_and_rejected[1]

    new_accounts_accepted_in_training_group = get_new_accounts_accepted_in_training_group(
        new_acts_accepted=new_accounts_accepted,
        curr_snapshot=current_snapshot,
        training_projects=training_groups
    )

    new_accounts_accepted_in_non_training_group = get_new_accounts_accepted_in_non_training_group(
        new_acts_accepted=new_accounts_accepted,
        curr_snapshot=current_snapshot,
        training_projects=training_groups
    )

    if args.recipients:
        report = """
        <p>Account Reporting: {start} to {end} ({dur} days)</p>
        <ul>
            <li>Accounts Requested: {num_nar} ({nar})</li>
            <li>Accounts Accepted: {num_naa} ({naa})</li>
                <ul>
                    <li>AND in Training Group: {num_naa_tr} ({naa_tr})</li>
                    <li>AND in Non Training Group: {num_naa_ntr} ({naa_ntr})</li>
                </ul>
            <li>Accounts Rejected: {num_rej} ({narej})</li>
        </ul>
        """.format(
            start=previous_snapshot["date"],
            end=current_snapshot["date"],
            dur=report_duration_in_days,
            num_nar=len(new_account_requests),
            nar=new_account_requests,
            num_naa=len(new_accounts_accepted),
            naa=new_accounts_accepted,
            num_naa_tr=len(new_accounts_accepted_in_training_group),
            naa_tr=new_accounts_accepted_in_training_group,
            num_naa_ntr=len(new_accounts_accepted_in_non_training_group),
            naa_ntr=new_accounts_accepted_in_non_training_group,
            num_rej=len(new_accounts_rejected),
            narej=new_accounts_rejected
        )

        send_report(recipients=args.recipients, msg_content=report)
