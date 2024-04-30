#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Any, cast, Mapping

from pydantic import BaseModel, ValidationError

from cmk.utils.config_validation_layer.type_defs import Omitted, OMITTED_FIELD
from cmk.utils.config_validation_layer.validation_utils import ConfigValidationError
from cmk.utils.labels import LabelGroups
from cmk.utils.rulesets.conditions import HostOrServiceConditions
from cmk.utils.rulesets.ruleset_matcher import RuleSpec, TagCondition
from cmk.utils.tags import TagGroupID


class RuleConditions(BaseModel):
    host_folder: str | Omitted = OMITTED_FIELD
    host_tags: Mapping[TagGroupID, TagCondition] | Omitted = OMITTED_FIELD
    host_label_groups: LabelGroups | Omitted = OMITTED_FIELD
    service_label_groups: LabelGroups | Omitted = OMITTED_FIELD
    service_description: HostOrServiceConditions | None | Omitted = OMITTED_FIELD
    host_name: HostOrServiceConditions | None | Omitted = OMITTED_FIELD


class RuleOptions(BaseModel):
    disabled: bool | Omitted = OMITTED_FIELD
    description: str | Omitted = OMITTED_FIELD
    comment: str | Omitted = OMITTED_FIELD
    docu_url: str | Omitted = OMITTED_FIELD
    predefined_condition_id: str | Omitted = OMITTED_FIELD


class Rule(BaseModel):
    id: str | Omitted = OMITTED_FIELD
    value: Any
    condition: RuleConditions
    options: RuleOptions | Omitted = OMITTED_FIELD


def validate_rule(rule: RuleSpec) -> None:
    rule_dict = cast(dict, rule)
    try:
        Rule(**rule_dict)
    except ValidationError as exc:
        raise ConfigValidationError(
            which_file="rules.mk",
            pydantic_error=exc,
            original_data=rule,
        )
