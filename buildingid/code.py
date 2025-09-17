# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/code.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

"""
UBID (Unique Building Identifier) code generation and manipulation.

This module provides functionality for creating, encoding, decoding, and validating
Unique Building Identifier (UBID) codes. UBIDs are based on Open Location Codes
(Plus Codes) but extended with building footprint information.

A UBID consists of:
- An Open Location Code (OLC) representing the building's center point
- Four numeric extents (North, East, South, West) indicating how far the building
  extends from the center point in each direction

Format: 'OLC-N-E-S-W' (e.g., '849VQJH6+95J-51-58-42-50')

Key Classes:
    Code: Type alias for UBID code strings
    CodeArea: Geographic area represented by a UBID code

Key Functions:
    encode(): Create a UBID from geographic coordinates
    decode(): Convert a UBID back to a geographic area
    isValid(): Validate a UBID code string

Example Usage:
    >>> from buildingid import code
    >>> 
    >>> # Encode coordinates to UBID
    >>> ubid = code.encode(41.707, -87.667, 41.708, -87.666, 41.7075, -87.6665)
    >>> print(ubid)
    >>> 
    >>> # Decode UBID back to area
    >>> area = code.decode(ubid)
    >>> print(f"Area: {area.latitudeLo},{area.longitudeLo} to {area.latitudeHi},{area.longitudeHi}")
    >>> 
    >>> # Validate a UBID
    >>> if code.isValid(ubid):
    >>>     print("Valid UBID")
"""

import re
import typing

from openlocationcode import openlocationcode

from .validators import isValidCodeArea, isValidCodeLength, isValidLatitude, isValidLatitudeCenter, isValidLongitude, isValidLongitudeCenter

SEPARATOR_ = '-'
"""Character used to separate components in UBID codes."""

FORMAT_STRING_ = '%s-%.0f-%.0f-%.0f-%.0f'
"""Format string for constructing UBID codes: 'OLC-N-E-S-W'."""

RE_PATTERN_ = re.compile(r''.join([
    r'^',
    r'(',
    r'[', re.escape(openlocationcode.CODE_ALPHABET_[0:9]), r'][', re.escape(openlocationcode.CODE_ALPHABET_[0:18]), r']',
    r'(?:',
    re.escape(openlocationcode.PADDING_CHARACTER_), r'{6}',
    re.escape(openlocationcode.SEPARATOR_),
    r'(?:',
    re.escape(openlocationcode.PADDING_CHARACTER_), r'{2,}',
    r')?',
    r'|',
    r'[', re.escape(openlocationcode.CODE_ALPHABET_), r']{2}',
    r'(?:',
    re.escape(openlocationcode.PADDING_CHARACTER_), r'{4}',
    re.escape(openlocationcode.SEPARATOR_),
    r'(?:',
    re.escape(openlocationcode.PADDING_CHARACTER_), r'{2,}',
    r')?',
    r'|',
    r'[', re.escape(openlocationcode.CODE_ALPHABET_), r']{2}',
    r'(?:',
    re.escape(openlocationcode.PADDING_CHARACTER_), r'{2}',
    re.escape(openlocationcode.SEPARATOR_),
    r'(?:',
    re.escape(openlocationcode.PADDING_CHARACTER_), r'{2,}',
    r')?',
    r'|',
    r'[', re.escape(openlocationcode.CODE_ALPHABET_), r']{2}',
    re.escape(openlocationcode.SEPARATOR_),
    r'(?:',
    re.escape(openlocationcode.PADDING_CHARACTER_), r'{2,}',
    r'|',
    r'[', re.escape(openlocationcode.CODE_ALPHABET_), r']{2,}',
    re.escape(openlocationcode.PADDING_CHARACTER_), r'*',
    r')?',
    r')',
    r')',
    r')',
    r')',
    re.escape(SEPARATOR_),
    r'(0|[1-9][0-9]*)',
    re.escape(SEPARATOR_),
    r'(0|[1-9][0-9]*)',
    re.escape(SEPARATOR_),
    r'(0|[1-9][0-9]*)',
    re.escape(SEPARATOR_),
    r'(0|[1-9][0-9]*)',
    r'$',
]), flags=re.IGNORECASE)
"""Compiled regex pattern for validating UBID code format."""

RE_GROUP_OPENLOCATIONCODE_ = 1
"""Regex group index for the Open Location Code component."""

RE_GROUP_NORTH_ = 2
"""Regex group index for the North extent value."""

RE_GROUP_EAST_ = 3
"""Regex group index for the East extent value."""

RE_GROUP_SOUTH_ = 4
"""Regex group index for the South extent value."""

RE_GROUP_WEST_ = 5
"""Regex group index for the West extent value."""

Code = typing.NewType('Code', str)
"""
Type alias for UBID code strings.

A UBID (Unique Building Identifier) code is a string that uniquely identifies
a building or structure using an Open Location Code (Plus Code) combined with
extent information in the format: 'OLC-N-E-S-W' where:
- OLC is an Open Location Code
- N, E, S, W are numeric extents (North, East, South, West)

Example: '849VQJH6+95J-51-58-42-50'
"""


class CodeArea(openlocationcode.CodeArea):
    """
    Represents a geographic area defined by a UBID code.

    Extends the Open Location Code CodeArea class to include UBID-specific
    functionality such as encoding to UBID format, calculating intersections,
    and computing Jaccard similarity coefficients.

    Attributes:
        centroid (openlocationcode.CodeArea): The center point of the area
        latitudeLo (float): Southern boundary latitude
        latitudeHi (float): Northern boundary latitude  
        longitudeLo (float): Western boundary longitude
        longitudeHi (float): Eastern boundary longitude
        codeLength (int): Precision length of the underlying OLC code
    """

    def __init__(self, centroid: openlocationcode.CodeArea, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.centroid = centroid

    @property
    def area(self) -> float:
        """
        Calculate the area of the CodeArea in square degrees.

        Returns:
            float: Area in square degrees (latitude degrees × longitude degrees)
        """
        height = float(self.latitudeHi - self.latitudeLo)
        width = float(self.longitudeHi - self.longitudeLo)

        return height * width

    def encode(self) -> Code:
        """
        Encode this CodeArea into a UBID code string.

        Returns:
            Code: UBID code string in format 'OLC-N-E-S-W'
        """
        return encode(self.latitudeLo, self.longitudeLo, self.latitudeHi, self.longitudeHi, self.centroid.latitudeCenter, self.centroid.longitudeCenter, codeLength=self.codeLength)

    def intersection(self, other: 'CodeArea') -> typing.Optional[typing.Tuple[float, float, float, float]]:
        """
        Calculate the intersection of this CodeArea with another CodeArea.

        Args:
            other (CodeArea): Another CodeArea to intersect with

        Returns:
            Optional[Tuple[float, float, float, float]]: Bounding box of intersection
                as (longitudeLo, latitudeLo, longitudeHi, latitudeHi) or None if no intersection
        """
        if other is None:
            return None

        latitudeLo = float(max(self.latitudeLo, other.latitudeLo))
        latitudeHi = float(min(self.latitudeHi, other.latitudeHi))
        longitudeLo = float(max(self.longitudeLo, other.longitudeLo))
        longitudeHi = float(min(self.longitudeHi, other.longitudeHi))

        if (latitudeLo > latitudeHi) or (longitudeLo > longitudeHi):
            return None

        return (longitudeLo, latitudeLo, longitudeHi, latitudeHi, )

    def jaccard(self, other: 'CodeArea') -> typing.Optional[float]:
        """
        Calculate the Jaccard similarity coefficient between this and another CodeArea.

        The Jaccard coefficient is defined as the area of intersection divided by
        the area of union: J(A,B) = |A ∩ B| / |A ∪ B|

        Args:
            other (CodeArea): Another CodeArea to compare with

        Returns:
            Optional[float]: Jaccard coefficient between 0 and 1, or None if no intersection
        """
        bbox = self.intersection(other)

        if bbox is None:
            return None

        area = (bbox[3] - bbox[1]) * (bbox[2] - bbox[0])

        return area / (self.area + other.area - area)

    def resize(self) -> 'CodeArea':
        """
        Create a new CodeArea that is half the size of this one, centered on the centroid.

        This shrinks the CodeArea by half the centroid cell size in each direction,
        effectively creating a smaller, more precise area representation.

        Returns:
            CodeArea: A new CodeArea with reduced bounds
        """
        halfHeight = float(self.centroid.latitudeHi - self.centroid.latitudeLo) / 2
        halfWidth = float(self.centroid.longitudeHi - self.centroid.longitudeLo) / 2

        return CodeArea(self.centroid, self.latitudeLo + halfHeight, self.longitudeLo + halfWidth, self.latitudeHi - halfHeight, self.longitudeHi - halfWidth, codeLength=self.codeLength)


def decode(code: Code) -> CodeArea:
    """
    Decode a UBID code string into a CodeArea object.

    Takes a UBID code in the format 'OLC-N-E-S-W' and converts it back into
    a geographic area with latitude/longitude boundaries.

    Args:
        code (Code): UBID code string to decode

    Returns:
        CodeArea: Geographic area represented by the UBID code

    Raises:
        ValueError: If the code is invalid or malformed
        AssertionError: If the decoded coordinates are invalid

    Example:
        >>> area = decode('849VQJH6+95J-51-58-42-50')
        >>> print(f"Bounds: {area.latitudeLo}, {area.longitudeLo} to {area.latitudeHi}, {area.longitudeHi}")
    """
    match = isValid_(code)

    if match is None:
        raise ValueError('buildingid.code.decode - Invalid code')

    codeAreaCenter = openlocationcode.decode(match.group(RE_GROUP_OPENLOCATIONCODE_))
    assert isValidCodeArea(codeAreaCenter), 'buildingid.code.decode - Invalid code area'

    codeAreaCenterHeight = codeAreaCenter.latitudeHi - codeAreaCenter.latitudeLo
    assert codeAreaCenterHeight >= 0, 'buildingid.code.decode - Invalid code - Negative height'

    codeAreaCenterWidth = codeAreaCenter.longitudeHi - codeAreaCenter.longitudeLo
    assert codeAreaCenterWidth >= 0, 'buildingid.code.decode - Invalid code - Negative width'

    latitudeLo = codeAreaCenter.latitudeLo - (int(match.group(RE_GROUP_SOUTH_)) * codeAreaCenterHeight)
    latitudeHi = codeAreaCenter.latitudeHi + (int(match.group(RE_GROUP_NORTH_)) * codeAreaCenterHeight)
    assert isValidLatitude(latitudeLo, latitudeHi), 'buildingid.code.decode - Invalid code - Invalid latitude coordinates'

    longitudeLo = codeAreaCenter.longitudeLo - (int(match.group(RE_GROUP_WEST_)) * codeAreaCenterWidth)
    longitudeHi = codeAreaCenter.longitudeHi + (int(match.group(RE_GROUP_EAST_)) * codeAreaCenterWidth)
    assert isValidLongitude(longitudeLo, longitudeHi), 'buildingid.code.decode - Invalid code - Invalid longitude coordinates'

    return CodeArea(codeAreaCenter, latitudeLo, longitudeLo, latitudeHi, longitudeHi, codeAreaCenter.codeLength)


def encode(latitudeLo: float, longitudeLo: float, latitudeHi: float, longitudeHi: float, latitudeCenter: float, longitudeCenter: float, codeLength: int = openlocationcode.PAIR_CODE_LENGTH_) -> Code:
    """
    Encode geographic coordinates into a UBID code string.

    Creates a UBID code from a bounding box and center point. The UBID format combines
    an Open Location Code (Plus Code) for the center point with extent information
    indicating how far the building extends in each direction.

    Args:
        latitudeLo (float): Southern boundary latitude in decimal degrees
        longitudeLo (float): Western boundary longitude in decimal degrees  
        latitudeHi (float): Northern boundary latitude in decimal degrees
        longitudeHi (float): Eastern boundary longitude in decimal degrees
        latitudeCenter (float): Center point latitude in decimal degrees
        longitudeCenter (float): Center point longitude in decimal degrees
        codeLength (int, optional): Precision of the OLC code. Defaults to PAIR_CODE_LENGTH_

    Returns:
        Code: UBID code string in format 'OLC-N-E-S-W'

    Raises:
        AssertionError: If any coordinates are invalid or out of range

    Example:
        >>> ubid = encode(41.707, -87.667, 41.708, -87.666, 41.7075, -87.6665)
        >>> print(ubid)  # '849VQJH6+95J-51-58-42-50'
    """
    assert isValidCodeLength(codeLength), 'buildingid.code.encode - Invalid code length'
    assert isValidLatitudeCenter(latitudeLo, latitudeHi, latitudeCenter), 'buildingid.code.encode - Invalid latitude coordinates'
    assert isValidLongitudeCenter(longitudeLo, longitudeHi, longitudeCenter), 'buildingid.code.encode - Invalid longitude coordinates'

    olcNortheast = openlocationcode.encode(latitudeHi, longitudeHi, codeLength=codeLength)
    codeAreaNortheast = openlocationcode.decode(olcNortheast)
    assert isValidCodeArea(codeAreaNortheast), 'buildingid.code.encode - Invalid code area (northeast)'

    olcSouthwest = openlocationcode.encode(latitudeLo, longitudeLo, codeLength=codeLength)
    codeAreaSouthwest = openlocationcode.decode(olcSouthwest)
    assert isValidCodeArea(codeAreaSouthwest), 'buildingid.code.encode - Invalid code area (southwest)'

    olcCenter = openlocationcode.encode(latitudeCenter, longitudeCenter, codeLength=codeLength)
    codeAreaCenter = openlocationcode.decode(olcCenter)
    assert isValidCodeArea(codeAreaCenter), 'buildingid.code.encode - Invalid code area (center)'

    codeAreaCenterHeight = codeAreaCenter.latitudeHi - codeAreaCenter.latitudeLo
    assert codeAreaCenterHeight >= 0, 'buildingid.code.encode - Invalid code - Negative height'

    codeAreaCenterWidth = codeAreaCenter.longitudeHi - codeAreaCenter.longitudeLo
    assert codeAreaCenterWidth >= 0, 'buildingid.code.encode - Invalid code - Negative width'

    olcCountNorth = (codeAreaNortheast.latitudeHi - codeAreaCenter.latitudeHi) / codeAreaCenterHeight
    assert olcCountNorth >= 0, 'buildingid.code.encode - Negative extent (north)'

    olcCountSouth = (codeAreaCenter.latitudeLo - codeAreaSouthwest.latitudeLo) / codeAreaCenterHeight
    assert olcCountSouth >= 0, 'buildingid.code.encode - Negative extent (south)'

    olcCountEast = (codeAreaNortheast.longitudeHi - codeAreaCenter.longitudeHi) / codeAreaCenterWidth
    assert olcCountEast >= 0, 'buildingid.code.encode - Negative extent (east)'

    olcCountWest = (codeAreaCenter.longitudeLo - codeAreaSouthwest.longitudeLo) / codeAreaCenterWidth
    assert olcCountWest >= 0, 'buildingid.code.encode - Negative extent (west)'

    return Code(FORMAT_STRING_ % (olcCenter, olcCountNorth, olcCountEast, olcCountSouth, olcCountWest))


def isValid(code: Code) -> bool:
    """
    Check if a UBID code string is valid.

    Validates that the code follows the correct UBID format and contains
    a valid Open Location Code component.

    Args:
        code (Code): UBID code string to validate

    Returns:
        bool: True if the code is valid, False otherwise

    Example:
        >>> isValid('849VQJH6+95J-51-58-42-50')
        True
        >>> isValid('invalid-code')
        False
    """
    return isValid_(code) is not None


def isValid_(code: Code) -> typing.Optional[typing.Match[str]]:
    """
    Internal validation function that returns regex match details.

    Performs detailed validation of a UBID code and returns the regex match
    object if valid, or None if invalid. This is used internally by other
    functions that need access to the parsed components.

    Args:
        code (Code): UBID code string to validate

    Returns:
        Optional[Match[str]]: Regex match object containing parsed components,
                             or None if the code is invalid
    """
    if code is None:
        return None

    match = RE_PATTERN_.match(str(code))

    if (match is None) or not openlocationcode.isValid(match.group(RE_GROUP_OPENLOCATIONCODE_)):
        return None

    return match
