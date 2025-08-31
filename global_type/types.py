from typing import Any, Dict, Optional, TypedDict



class HeadingDict(TypedDict):
    H1: str
    H2: str
    H3: str
    H4: str
    H5: str
    H6: str


class MetadataDict(TypedDict, total=False):
    description: str
    keywords: Optional[str]
    author: Optional[str]
    canonical: Optional[str]
    og_tags: Dict[str, Any]
    twitter_tags: Dict[str, Any]
    schema_org: Optional[Any]

class PageMeta(TypedDict):
    title: str
    description: str
    keywords: str
    metadata: MetadataDict