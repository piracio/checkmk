#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from typing import Mapping, Optional, Protocol


class HTTPProxyConfig(Protocol):
    def to_requests_proxies(self) -> Optional[Mapping[str, str]]:
        ...

    def serialize(self) -> str:
        ...

    # For unit tests
    def __eq__(self, o: object) -> bool:
        ...


class EnvironmentProxyConfig:
    SERIALIZED = "FROM_ENVIRONMENT"

    def to_requests_proxies(self) -> None:
        return None

    def serialize(self) -> str:
        return self.SERIALIZED

    def __eq__(self, o: object) -> bool:
        return isinstance(o, EnvironmentProxyConfig)


class NoProxyConfig:
    SERIALIZED = "NO_PROXY"

    def to_requests_proxies(self) -> None:
        return None

    def serialize(self) -> str:
        return self.SERIALIZED

    def __eq__(self, o: object) -> bool:
        return isinstance(o, NoProxyConfig)


class ExplicitProxyConfig:
    def __init__(self, url: str) -> None:
        self._url = url

    def to_requests_proxies(self) -> Mapping[str, str]:
        return {
            "http": self._url,
            "https": self._url,
        }

    def serialize(self) -> str:
        return self._url

    def __eq__(self, o: object) -> bool:
        return isinstance(o, ExplicitProxyConfig) and self._url == o._url


def deserialize_http_proxy_config(serialized_config: Optional[str]) -> HTTPProxyConfig:
    """
    >>> deserialize_http_proxy_config("FROM_ENVIRONMENT") == EnvironmentProxyConfig()
    True
    >>> deserialize_http_proxy_config("NO_PROXY") == NoProxyConfig()
    True
    >>> deserialize_http_proxy_config("abc123") == ExplicitProxyConfig("abc123")
    True
    """
    if serialized_config is None:
        return EnvironmentProxyConfig()
    if serialized_config == EnvironmentProxyConfig.SERIALIZED:
        return EnvironmentProxyConfig()
    if serialized_config == NoProxyConfig.SERIALIZED:
        return NoProxyConfig()
    return ExplicitProxyConfig(serialized_config)
