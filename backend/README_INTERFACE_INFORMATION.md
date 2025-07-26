# OBIR-Tree-Web 前后端数据接口与C++对接说明

## 目录
1. [接口总览](#接口总览)
2. [数据交换文件说明](#数据交换文件说明)
3. [接口详细说明](#接口详细说明)
4. [C++后端开发注意事项](#c后端开发注意事项)

---

## 接口总览

| 交互内容           | 前端API/文件                | C++需处理/生成的文件                | 说明 |
|--------------------|-----------------------------|--------------------------------------|------|
| 检索查询参数       | POST /api/query-results     | data/search_query.json               | 前端发起检索时写入，C++需读取并据此生成新数据 |
| IR-Tree结构        | POST /api/ir-tree-svg       | data/ir_tree_data.json               | C++生成IR-Tree结构数据，Python生成SVG |
| IR-OBIR映射关系    | POST /api/ir-obir-relation-svg | data/ir_obir_mapping.json, data/ir_obir_annotations.json | C++生成映射关系和标注数据 |
| 逻辑路径           | POST /api/ir-logic-path-svg  | data/ir_logic_path_data.json         | C++生成逻辑路径数据 |
| OBIR-Tree实时路径  | POST /api/obir-tree-realtime | data/obir_tree_current.json, data/obir_tree_previous.json | C++生成/更新OBIR-Tree结构数据（支持diff） |
| 检索结果           | POST /api/query-results     | C++可直接返回或写入data/query_results.json | C++返回top-k空间文本结果（可选） |

---

## 数据交换文件说明

### 1. 检索查询参数（search_query.json）
- 路径：`backend/data/search_query.json`
- 由前端每次搜索时写入，C++需监听并据此生成/更新其它数据文件
- 格式示例：
```json
{
  "query": "北京大学",
  "lng": "116.404",
  "lat": "39.915",
  "topK": 5
}
```

### 2. IR-Tree结构数据（ir_tree_data.json）
- 路径：`backend/data/ir_tree_data.json`
- 由C++生成，Python脚本读取并生成SVG
- 格式示例：
```json
{
  "nodes": [ { "id": "n1", "value": "Root", "level": 0, ... } ],
  "edges": [ { "from": "n1", "to": "n2" } ],
  "metadata": { ... }
}
```

### 3. IR-OBIR映射关系与标注（ir_obir_mapping.json, ir_obir_annotations.json）
- 路径：`backend/data/ir_obir_mapping.json`, `backend/data/ir_obir_annotations.json`
- 由C++生成，Python脚本读取
- 映射关系格式：
```json
{
  "ir_nodes": [ ... ],
  "obir_nodes": [ ... ],
  "relations": [ { "ir_id": "...", "obir_id": "..." } ]
}
```
- 标注格式：
```json
[
  { "id": "obir1", "desc": "..." }, ...
]
```

### 4. 逻辑路径数据（ir_logic_path_data.json）
- 路径：`backend/data/ir_logic_path_data.json`
- 由C++生成，Python脚本读取
- 格式示例：
```json
{
  "nodes": [ ... ],
  "edges": [ ... ],
  "logic_path": [ "n1", "n2", ... ],
  "query_info": { ... }
}
```

### 5. OBIR-Tree实时路径数据（obir_tree_current.json, obir_tree_previous.json）
- 路径：`backend/data/obir_tree_current.json`, `backend/data/obir_tree_previous.json`
- 由C++生成，Python脚本读取，支持diff高亮
- 格式示例：
```json
{
  "nodes": [ { "id": "...", "value": "...", "level": 0, ... } ],
  "edges": [ { "from": "...", "to": "..." } ],
  "metadata": { ... }
}
```

### 6. 检索结果数据（可选，query_results.json）
- 路径：`backend/data/query_results.json`
- C++可直接写入，或由Python/前端模拟
- 格式示例：
```json
[
  {
    "title": "...",
    "description": "...",
    "relevance": 95,
    "location": "...",
    "distance": 0.2,
    "type": "教育机构"
  }, ...
]
```

---

## 接口详细说明

### 1. 检索查询参数传递
- 前端每次搜索时，POST `/api/query-results`，参数会被写入`search_query.json`
- C++需监听此文件，解析参数后生成/更新其它数据文件

### 2. IR-Tree结构、IR-OBIR关系、逻辑路径、OBIR-Tree实时路径
- 前端每次刷新流程节点时，自动请求对应API，Python脚本读取C++生成的数据文件，生成SVG返回前端
- C++需保证数据文件及时更新，且格式正确

### 3. 检索结果
- 可选：C++可直接返回top-k结果，或写入`query_results.json`，由Python/前端读取

---

## C++后端开发注意事项

1. **所有数据文件需写入`OBIR-Tree-Web/backend/data/`目录下**，文件名需与前端/后端约定一致。
2. **JSON格式需严格遵循示例**，避免字段缺失或类型错误。
3. **每次前端搜索后，C++应尽快根据`search_query.json`生成/更新所有相关数据文件**，以保证前端刷新时能获取到最新内容。
4. **如需扩展其它数据交互，可参考上述模式，前端/后端均易于扩展。**
5. **建议C++端监听文件变化或定时轮询`search_query.json`，实现准实时响应。**

---

如有更多接口需求或格式变更，请及时与前端/后端开发协商！
