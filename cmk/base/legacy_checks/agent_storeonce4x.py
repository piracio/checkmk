#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from typing import Any, Mapping, Sequence

from cmk.base.check_api import passwordstore_get_cmdline
from cmk.base.config import special_agent_info


def agent_storeonce4x_arguments(
    params: Mapping[str, Any], hostname: str, ipaddress: str | None
) -> Sequence[str | tuple[str, str, str]]:
    args = [
        params["user"],
        passwordstore_get_cmdline("%s", params["password"]),
        hostname,
    ]

    if "cert" in params and params["cert"] is True:
        args.append("--verify_ssl")

    return args


special_agent_info["storeonce4x"] = agent_storeonce4x_arguments
