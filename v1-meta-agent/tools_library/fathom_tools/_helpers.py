"""
Internal helper functions for Fathom tools
"""
from typing import List


def extract_discussion_points(markdown: str) -> List[str]:
    """
    Internal helper: Extract discussion points from markdown summary.
    """
    things_discussed = []
    
    if not markdown:
        return things_discussed
    
    if "## Things Discussed" in markdown or "## Discussion" in markdown:
        lines = markdown.split('\n')
        in_discussion_section = False
        
        for line in lines:
            if "## Things Discussed" in line or "## Discussion" in line:
                in_discussion_section = True
                continue
            elif line.startswith("## "):
                in_discussion_section = False
            elif in_discussion_section and line.strip().startswith("-"):
                point = line.strip().lstrip("- ").strip()
                if point:
                    things_discussed.append(point)
    
    return things_discussed
