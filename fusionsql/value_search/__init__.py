"""
值匹配模块

提供两种数据库值相似度搜索功能：
- BGE + FAISS: 语义匹配（推荐）
- MinHash LSH: 字符级匹配（旧版）

使用方法:

1. 构建 BGE 索引（推荐）:
   ```python
   from fusionsql.value_search import build_bge_value_index
   build_bge_value_index(output_dir="./bge_value_index")
   ```

2. BGE 搜索:
   ```python
   from fusionsql.value_search import BGEValueSearcher
   searcher = BGEValueSearcher("./bge_value_index")
   results = searcher.search("ciscoA")
   ```

3. LSH 搜索（旧版，兼容）:
   ```python
   from fusionsql.value_search import ValueSearcher
   searcher = ValueSearcher("./lsh_index")
   results = searcher.search("ciscoA")
   ```
"""

# BGE 模块（推荐）
from .bge_preprocess import build_bge_value_index
from .bge_search import BGEValueSearcher, load_bge_searcher

# LSH 模块（旧版，保留兼容）
from .preprocess import build_lsh_index, make_lsh
from .search import ValueSearcher, load_searcher

__all__ = [
    # BGE（推荐）
    "build_bge_value_index",
    "BGEValueSearcher",
    "load_bge_searcher",
    # LSH（兼容）
    "build_lsh_index",
    "make_lsh",
    "ValueSearcher",
    "load_searcher",
]
