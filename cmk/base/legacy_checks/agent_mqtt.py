#!/usr/bin/env python3
# Copyright (C) 2021 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from typing import Any, Mapping, Sequence

from cmk.base.check_api import passwordstore_get_cmdline
from cmk.base.config import special_agent_info


def agent_mqtt_arguments(
    params: Mapping[str, Any], hostname: str, ipaddress: str | None
) -> Sequence[str | tuple[str, str, str]]:
    args = []
    for key in sorted(k for k in params if k != "address"):
        val = (
            passwordstore_get_cmdline("%s", params[key]) if key == "password" else f"{params[key]}"
        )
        args += [f"--{key}", val]

    args += [params.get("address") or ipaddress or hostname]

    return args


special_agent_info["mqtt"] = agent_mqtt_arguments
