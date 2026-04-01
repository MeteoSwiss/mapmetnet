"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: NASA GIBS tools
"""

# Import from Python
from typing import Optional
import logging
from pathlib import Path
import numpy as np
import cairosvg
from PIL import Image

# Import from this package
from .logger import log_func_call

# Instantiate the module logger
logger = logging.getLogger(__name__)


@log_func_call(logger)
def get_cb_img(cb_name: str, write_loc: Optional[Path] = Path('.')) -> np.ndarray:
    """ Basic utility routine to fetch a colorbar from NASA GIBS in SVG format, convert it to
    png, and return it as a numpy array.

    Args:
        cb_name (str): the name of the colorbar file. Should match a file in
            https://gitc.earthdata.nasa.gov/legends
        write_loc (pathlib.Path, optional): location where the NASA GIBS image will be stored
            temporarily. Defaults to Path('.').

    Returns:
        np.ndarray: the colorbar image as numpy array, suitable for imshow plotting.

    Note:
        The colorbar will be save to disc temporarily.

    """

    # Fetch the colorbar as SVG from NASA, convert it to png with decent DPI, and store it locally.
    cb_fn = write_loc / 'mapmetnet_GIBS_cb.png'
    cairosvg.svg2png(url=f'https://gitc.earthdata.nasa.gov/legends/{cb_name}',
                     write_to=str(cb_fn), dpi=300)

    # Load the png, and get it ready for plotting
    cb_img = np.asarray(Image.open(cb_fn))

    # Delete the file
    cb_fn.unlink()

    return cb_img
