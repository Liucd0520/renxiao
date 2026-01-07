"""
LSH 值匹配模块

提供基于 MinHash LSH 的数据库值相似度搜索功能。

使用方法:

1. 构建索引:
   ```python
   from fusionsql.value_search import build_lsh_index
   build_lsh_index(output_dir="./lsh_index")
   ```

2. 搜索:
   ```python
   from fusionsql.value_search import ValueSearcher
   searcher = ValueSearcher("./lsh_index")
   results = searcher.search("ciscoA")
   ```
"""

from .preprocess import build_lsh_index, make_lsh
from .search import ValueSearcher, load_searcher

__all__ = [
    "build_lsh_index",
    "make_lsh",
    "ValueSearcher",
    "load_searcher",
]
