"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

# Import from Python
import logging

# Import from this module
from mapmetnet.logger import log_func_call


logger = logging.getLogger(__name__)


# Based on the reply on SO: https://stackoverflow.com/questions/53125305/
def test_log(caplog):
    """ Test the log_func_call decorator living in logger.py """

    @log_func_call(logger)
    def dummy_func(input_value: float) -> int:
        return int(input_value)

    with caplog.at_level(logging.INFO):
        dummy_func(3.2)

    assert "Executing dummy_func() ..." in caplog.text

    with caplog.at_level(logging.DEBUG):
        dummy_func(3.2)

    assert " ... with the following input: {'input_value': 3.2}" in caplog.text
