"""
{{ PROJECT }}
=============

{{ DESCRIPTION }}
"""

import logging

from .version import version as __version__

logger = logging.getLogger(__name__)
try:
    # Prevent output if no handler set
    logger.addHandler(logging.NullHandler())
except AttributeError:
    pass

__copyright__ = "{{ COPYRIGHT YEARS }}, Applied Brain Research"
__license__ = "Free for non-commercial use; see LICENSE.rst"
