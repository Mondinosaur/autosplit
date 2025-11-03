"""Validation functions for AutoSplit."""
from __future__ import annotations
from typing import Any, List, Optional

def validate_group(df: Any, 
                  min_images: int, 
                  image_cols: Optional[List[str]]) -> List[str]:
    """Validate a group DataFrame against requirements.
    
    Args:
        df: Input DataFrame to validate
        min_images: Minimum number of image URLs required
        image_cols: List of column names containing image URLs
        
    Returns:
        list: List of warning messages (empty if validation passes)
    """
    warnings = []
    if image_cols:
        count = 0
        for c in image_cols:
            if c in df.columns:
                count += df[c].notna().sum()
        if count < min_images:
            warnings.append(f"Less than {min_images} image URLs ({count})")
    return warnings