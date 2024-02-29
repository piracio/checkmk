#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence

import pytest

from cmk.plugins.mail.server_side_calls.mailboxes import active_check_mailboxes
from cmk.server_side_calls.v1 import HostConfig, IPv4Config, Secret

HOST_CONFIG = HostConfig(
    name="host",
    ipv4_config=IPv4Config(address="127.0.0.1"),
    macros={"$HOSTNAME$": "host"},
)


@pytest.mark.parametrize(
    "params,expected_args",
    [
        (
            {
                "service_description": "Mailboxes",
                "fetch": (
                    "IMAP",
                    {
                        "server": "foo",
                        "connection": {
                            "disable_tls": True,
                            "port": 143,
                        },
                        "auth": ("basic", ("hans", Secret(0))),
                    },
                ),
            },
            [
                "--fetch-protocol=IMAP",
                "--fetch-server=foo",
                "--fetch-port=143",
                "--fetch-username=hans",
                Secret(0, "--fetch-password=%s"),
            ],
        ),
        (
            {
                "service_description": "Mailboxes",
                "fetch": (
                    "EWS",
                    {
                        "server": "foo",
                        "connection": {},
                        "auth": ("basic", ("hans", Secret(1))),
                    },
                ),
            },
            [
                "--fetch-protocol=EWS",
                "--fetch-server=foo",
                "--fetch-tls",
                "--fetch-username=hans",
                Secret(1, "--fetch-password=%s"),
            ],
        ),
        (
            {
                "service_description": "Mailboxes",
                "fetch": (
                    "EWS",
                    {
                        "server": "foo",
                        "connection": {},
                        "auth": (
                            "oauth2",
                            ("client_id", Secret(0), "tenant_id"),
                        ),
                    },
                ),
            },
            [
                "--fetch-protocol=EWS",
                "--fetch-server=foo",
                "--fetch-tls",
                "--fetch-client-id=client_id",
                Secret(0, "--fetch-client-secret=%s"),
                "--fetch-tenant-id=tenant_id",
            ],
        ),
        pytest.param(
            {
                "service_description": "Mailboxes",
                "fetch": (
                    "IMAP",
                    {
                        "server": "$HOSTNAME$",
                        "connection": {
                            "disable_tls": True,
                            "disable_cert_validation": True,
                            "port": 10,
                        },
                        "auth": ("basic", ("user", Secret(1))),
                    },
                ),
                "connect_timeout": 10,
                "age": (0, 0),
                "age_newest": (0, 0),
                "count": (0, 0),
                "mailboxes": ["mailbox1", "mailbox2"],
                "retrieve_max": 100,
            },
            [
                "--fetch-protocol=IMAP",
                "--fetch-server=host",
                "--fetch-disable-cert-validation",
                "--fetch-port=10",
                "--fetch-username=user",
                Secret(1, "--fetch-password=%s"),
                "--connect-timeout=10",
                "--retrieve-max=100",
                "--warn-age-oldest=0",
                "--crit-age-oldest=0",
                "--warn-age-newest=0",
                "--crit-age-newest=0",
                "--warn-count=0",
                "--crit-count=0",
                "--mailbox=mailbox1",
                "--mailbox=mailbox2",
            ],
            id="all parameters",
        ),
    ],
)
def test_check_mailboxes_argument_parsing(
    params: Mapping[str, object], expected_args: Sequence[str]
) -> None:
    """Tests if all required arguments are present."""
    commands = list(active_check_mailboxes(params, HOST_CONFIG, {}))

    assert len(commands) == 1
    assert commands[0].command_arguments == expected_args
    assert commands[0].service_description == "Mailboxes"
