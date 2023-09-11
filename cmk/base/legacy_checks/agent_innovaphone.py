#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from typing import Any, Mapping, Sequence

from cmk.base.check_api import passwordstore_get_cmdline
from cmk.base.config import special_agent_info


def agent_innovaphone_arguments(
    params: Mapping[str, Any], hostname: str, ipaddress: str | None
) -> Sequence[str | tuple[str, str, str]]:
    auth_info = params["auth_basic"]
    username = auth_info["username"]
    password = passwordstore_get_cmdline("%s", auth_info["password"])
    args = [hostname, username, password]
    protocol = params.get("protocol")
    if protocol:
        args.extend(["--protocol", protocol])
    if params.get("no-cert-check"):
        args.append("--no-cert-check")
    return args


special_agent_info["innovaphone"] = agent_innovaphone_arguments
