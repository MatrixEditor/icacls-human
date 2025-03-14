#!/usr/bin/env python3
# icacls-to-human: Converts icacls output to human-readable format
#
# Copyright (C) MatrixEditor 2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Description:
#   Converts output from icacls to human-readable format by providing
#   more information about file or directory permissions.
#
# Author:
#   MatrixEditor
#
# References:
#   - https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls
import logging
import sys
import re

try:
    from importlib.metadata import version

    TOOL_VERSION = version("icacls2h")
except ImportError:  # PackageNotFoundError is subclass of ImportError
    TOOL_VERSION = None


# --- Logger Configuration ---
class LoggerFormatter(logging.Formatter):
    def __init__(self, ts=False):
        fmt = "%(prefix)s %(message)s"
        if ts:  # timestamp
            fmt = f"[%(asctime)-15s] {fmt}"
        logging.Formatter.__init__(self, fmt, None)

    def format(self, record):
        match record.levelno:
            case logging.DEBUG:
                record.prefix = "[+]"
            case logging.INFO:
                record.prefix = "[*]"
            case logging.WARNING:
                record.prefix = "[!]"
            case _:
                record.prefix = "[-]"
        return logging.Formatter.format(self, record)


# --- DACL Format ---
# See Microsoft documentation:
#
# According to the documentation, a '<perm>' option is a permission mask that can be
# specified in one of the following forms:
#
# 1. A sequence of simple rights (basic permissions):
DACL_BASIC_RIGHTS = {
    "F": "Full access",
    "M": "Modify access",
    "RX": "Read and execute access",
    "R": "Read-only access",
    "W": "Write-only access",
}

# 2. A comma-separated list in parenthesis of specific rights (advanced permissions):
DACL_ADVANCED_RIGHTS = {
    "D": "Delete",
    "RC": "Read control (read permissions)",
    "WDAC": "Write DAC (change permissions)",
    "WO": "Write owner (take ownership)",
    "S": "Synchronize",
    "AS": "Access system security",
    "MA": "Maximum allowed",
    "GR": "Generic read",
    "GW": "Generic write",
    "GE": "Generic execute",
    "GA": "Generic all",
    "RD": "Read data/list directory",
    "WD": "Write data/add file",
    "AD": "Append data/add subdirectory",
    "REA": "Read extended attributes",
    "WEA": "Write extended attributes",
    "X": "Execute/traverse",
    "DC": "Delete child",
    "RA": "Read attributes",
    "WA": "Write attributes",
}

# 3. Inheritance rights may precede either <perm> form:
DACL_INHERITANCE_RIGHTS = {
    "I": (
        "Inherit",
        "ACE inherited from the parent container.",
        False,
    ),
    "OI": (
        "Object Inherit",
        "Objects in this container will inherit this ACE.",
        True,
    ),
    "CI": (
        "Container Inherit",
        "Containers in this parent container will inherit this ACE.",
        True,
    ),
    "IO": (
        "Inherit Only",
        "ACE inherited from the parent container, but does not apply to the object itself.",
        True,
    ),
    "NP": (
        "Do Not Propagate Inherit",
        (
            "Do not propagate inherit. ACE inherited by containers and objects from "
            "the parent container, but does not propagate to nested containers."
        ),
        True,
    ),
}

# We can capture all access rights with the following pattern
RE_ACE = re.compile(r"\(([\w,]+)\)")


def pprint_dacl(name: str, dacl_list: list[str]) -> None:
    logging.info("%s Rights:", name)
    logging.debug("Processing DACL list: %s", name)
    print("ACE Name".ljust(20), "Description")
    print(("-" * 8).ljust(20), "-" * 11)
    for ace_id, desc in dacl_list.items():
        if isinstance(desc, tuple):
            desc, *_ = desc
        print(ace_id.ljust(20), desc)

    logging.debug("Finished processing DACL list: %s", name)
    print()


if __name__ == "__main__":
    # Setup parser and arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Converts icacls output to human-readable format",
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    parser.add_argument(
        "-timestamp",
        action="store_true",
        help="include timestamp in logging output",
    )
    parser.add_argument(
        "-debug",
        action="store_true",
        help="enable debug logging",
    )
    parser.add_argument(
        "-list",
        help="Lists all permissions of the specified type together with their identifier.",
        type=str,
        choices=["basic", "advanced", "inheritance", "all"],
    )
    parser.add_argument(
        "dacl_string",
        nargs="?",
        metavar="DACL_STRING",
        type=str,
        default=None,
        help=(
            "Input DACL string to process. If not specified, will read from stdin. "
            "This string may contain multiple DACLs separated by newlines. "
        ),
    )
    parser.add_argument(
        "-q",
        "-no-banner",
        action="store_true",
        dest="no_banner",
        help="disable banner / version info at startup",
    )
    parser.add_argument(
        "-details",
        action="store_true",
        help="display more details about the converted DACLs",
    )

    argv = parser.parse_args()
    # initialize logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(LoggerFormatter(ts=argv.timestamp))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
    if argv.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if argv.dacl_string and argv.list:
        logging.error(
            "Cannot list DACLs and process input at the same time. "
            "Please specify either the list option or the input string, but not both."
        )
        sys.exit(1)

    if TOOL_VERSION and not argv.no_banner:
        print(f"icacls2h v{TOOL_VERSION} - by MatrixEditor\n")

    match argv.list:
        case "all":
            pprint_dacl("Basic", DACL_BASIC_RIGHTS)
            pprint_dacl("Advanced", DACL_ADVANCED_RIGHTS)
            pprint_dacl("Inheritance", DACL_INHERITANCE_RIGHTS)
        case "advanced":
            pprint_dacl("Advanced", DACL_ADVANCED_RIGHTS)
        case "inheritance":
            pprint_dacl("Inheritance", DACL_INHERITANCE_RIGHTS)
        case "basic":
            pprint_dacl("Basic", DACL_BASIC_RIGHTS)

    if argv.list is not None:
        sys.exit(0)

    if not argv.dacl_string:
        logging.debug("Reading input from stdin...")
        try:
            argv.dacl_string = sys.stdin.read()
        except KeyboardInterrupt:
            logging.info(
                "Unable to read input from stdin. Please specify an input DACL string."
            )
            sys.exit(1)

    logging.debug(
        "Processing input DACL string with %s lines.", argv.dacl_string.count("\n") or 1
    )
    target_file = None
    is_first_line = True
    for line in argv.dacl_string.splitlines():
        ace_list = RE_ACE.findall(line)
        target_account = None
        current_dacl_string = line
        if ":" in line:
            # output contains at least the identity group
            target, current_dacl_string = line.rsplit(":", 1)
            if is_first_line and " " in target:
                target_file, target_account = target.rsplit(" ", 1)
                # REVISIT: ignore groups with space in their name
                if not target_file.endswith("NT"):
                    target_account = target
                    target_file = None
                else:
                    target_account = f"NT {target_account}"
                    target_file = target_file.removesuffix("NT").strip()
            else:
                target_account = target

        if len(ace_list) > 0:
            if target_file and is_first_line:
                logging.info("Target: %s\n", target_file)

            if target_account:
                logging.info("SID Name: %s", target_account.strip())

            logging.info(f"DACL: {current_dacl_string.strip()!r}")
            first_perm = True
            first_inherit = True
            for ace in ace_list:
                if ace in DACL_INHERITANCE_RIGHTS:
                    if first_inherit:
                        logging.info("Inheritance Rights:")
                        first_inherit = False

                    name, desc, dir_only = DACL_INHERITANCE_RIGHTS[ace]
                    print(f"\t+ ({ace}): {name} (dir-only: {dir_only})")
                    if argv.details:
                        print(f"\t\t{desc!r}")

                else:
                    if first_perm:
                        logging.info("Permissions:")
                        first_perm = False

                    for ace_key in ace.split(","):
                        # won't be a key for inheritance rights
                        desc = DACL_BASIC_RIGHTS.get(ace_key, DACL_ADVANCED_RIGHTS.get(ace_key))
                        print(f"\t+ ({ace_key}): {desc}")

            # make space between each DACL
            print()

        if is_first_line:
            is_first_line = False
