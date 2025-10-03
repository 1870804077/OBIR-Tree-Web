# OBIR-Tree-Web 前后端数据接口与C++对接详细说明

## 目录
1. [接口与数据文件总览](#接口与数据文件总览)
2. [各数据文件详细说明](#各数据文件详细说明)
3. [典型流程举例](#典型流程举例)
4. [C++后端开发注意事项](#c后端开发注意事项)

---

## 接口与数据文件总览

| 交互内容           | 由谁生成/消费         | 前端API/文件                | C++需处理/生成的文件                | 作用/用途 |
|--------------------|----------------------|-----------------------------|--------------------------------------|-----------|
| 检索查询参数       | 前端生成，C++消费    | POST /api/query-results     | data/search_query.json               | 前端发起检索时写入，C++读取后生成/更新其它数据 |
| IR-Tree结构        | C++生成，Python消费  | POST /api/ir-tree-svg       | data/ir_tree_data.json               | C++生成IR-Tree结构数据，Python生成SVG供前端展示 |
| IR-OBIR映射关系    | C++生成，Python消费  | POST /api/ir-obir-relation-svg | data/ir_obir_mapping.json, data/ir_obir_annotations.json | C++生成映射关系和标注数据，Python生成SVG及标注 |
| 逻辑路径           | C++生成，Python消费  | POST /api/ir-logic-path-svg  | data/ir_logic_path_data.json         | C++生成逻辑路径数据，Python生成高亮路径SVG |
| OBIR-Tree实时路径  | C++生成，Python消费  | POST /api/obir-tree-realtime | data/obir_tree_current.json, data/obir_tree_previous.json | C++生成/更新OBIR-Tree结构数据，Python对比差异并生成SVG |
| 检索结果           | C++生成/前端消费     | POST /api/query-results     | data/query_results.json（可选）      | C++可直接返回top-k空间文本结果，前端展示 |

---

## 各数据文件详细说明

### 1. 检索查询参数（search_query.json）
- **由谁生成/消费**：前端生成，C++消费
- **作用/用途**：前端每次发起检索时写入，C++读取后据此生成/更新其它数据文件（如IR-Tree、OBIR-Tree等）
- **字段说明**：
  | 字段名   | 类型   | 含义           | 示例         |
  |----------|--------|----------------|--------------|
  | query    | string | 检索关键词     | "北京大学"   |
  | lng      | string/float | 经度      | "116.404"   |
  | lat      | string/float | 纬度      | "39.915"    |
  | topK     | int    | 返回结果数量   | 5            |
- **示例**：
```json
{
  "query": "北京大学",
  "lng": "116.404",
  "lat": "39.915",
  "topK": 5
}
```

### 2. IR-Tree结构数据（ir_tree_data.json）
- **由谁生成/消费**：C++生成，Python消费
- **作用/用途**：C++根据检索参数生成IR-Tree结构，Python脚本读取并生成SVG，前端展示树结构
- **字段说明**：
  | 字段名   | 类型   | 含义           | 示例         |
  |----------|--------|----------------|--------------|
  | nodes    | array  | 节点列表       | [{...}, ...] |
  | edges    | array  | 边列表         | [{...}, ...] |
  | metadata | object | 其它元数据     | {...}        |
- **节点对象**：
  | 字段名   | 类型   | 含义           | 示例         |
  |----------|--------|----------------|--------------|
  | id       | string | 节点唯一标识   | "n1"         |
  | value    | string | 节点内容/值    | "Root"       |
  | level    | int    | 层级           | 0            |
  | ...      | ...    | 可扩展         |              |
- **边对象**：
  | 字段名   | 类型   | 含义           | 示例         |
  |----------|--------|----------------|--------------|
  | from     | string | 起点节点id     | "n1"         |
  | to       | string | 终点节点id     | "n2"         |
- **示例**：
```json
{
  "nodes": [ { "id": "n1", "value": "Root", "level": 0 }, { "id": "n2", "value": "A", "level": 1 } ],
  "edges": [ { "from": "n1", "to": "n2" } ],
  "metadata": { "tree_type": "IR-Tree" }
}
```

### 3. IR-OBIR映射关系与标注（ir_obir_mapping.json, ir_obir_annotations.json）
- **由谁生成/消费**：C++生成，Python消费
- **作用/用途**：C++生成IR节点与OBIR节点的映射关系，以及每个节点/映射的标注信息，Python生成SVG及右侧标注
- **映射关系文件（ir_obir_mapping.json）字段说明**：
  | 字段名     | 类型   | 含义           | 示例         |
  |------------|--------|----------------|--------------|
  | ir_nodes   | array  | IR节点列表     | [{...}]      |
  | obir_nodes | array  | OBIR节点列表   | [{...}]      |
  | relations  | array  | 映射关系       | [{...}]      |
- **relations对象**：
  | 字段名   | 类型   | 含义           | 示例         |
  |----------|--------|----------------|--------------|
  | ir_id    | string | IR节点id       | "ir1"        |
  | obir_id  | string | OBIR节点id     | "obir1"      |
- **标注文件（ir_obir_annotations.json）字段说明**：
  | 字段名   | 类型   | 含义           | 示例         |
  |----------|--------|----------------|--------------|
  | id       | string | 节点/映射id    | "obir1"      |
  | desc     | string | 标注内容       | "OBIR节点1"  |
- **示例**：
```json
{
  "ir_nodes": [ { "id": "ir1", "value": "IR节点1" } ],
  "obir_nodes": [ { "id": "obir1", "value": "OBIR节点1" } ],
  "relations": [ { "ir_id": "ir1", "obir_id": "obir1" } ]
}
```
```json
[
  { "id": "obir1", "desc": "OBIR节点1: 说明..." }
]
```

### 4. 逻辑路径数据（ir_logic_path_data.json）
- **由谁生成/消费**：C++生成，Python消费
- **作用/用途**：C++根据检索参数和SGX解密结果生成IR-Tree的逻辑路径，Python高亮路径生成SVG
- **字段说明**：
  | 字段名     | 类型   | 含义           | 示例         |
  |------------|--------|----------------|--------------|
  | nodes      | array  | 节点列表       | [{...}]      |
  | edges      | array  | 边列表         | [{...}]      |
  | logic_path | array  | 路径节点id序列 | ["n1", ...]  |
  | query_info | object | 查询参数信息   | {...}        |
- **示例**：
```json
{
  "nodes": [ { "id": "n1", "value": "Root" }, { "id": "n2", "value": "A" } ],
  "edges": [ { "from": "n1", "to": "n2" } ],
  "logic_path": [ "n1", "n2" ],
  "query_info": { "query": "北京大学", "topK": 5 }
}
```

### 5. OBIR-Tree实时路径数据（obir_tree_current.json, obir_tree_previous.json）
- **由谁生成/消费**：C++生成，Python消费
- **作用/用途**：C++每次检索/更新后生成当前和上一次OBIR-Tree结构，Python对比两次结构差异，生成高亮diff的SVG
- **字段说明**：
  | 字段名   | 类型   | 含义           | 示例         |
  |----------|--------|----------------|--------------|
  | nodes    | array  | 节点列表       | [{...}]      |
  | edges    | array  | 边列表         | [{...}]      |
  | metadata | object | 其它元数据     | {...}        |
- **节点对象**同IR-Tree
- **示例**：
```json
{
  "nodes": [ { "id": "n1", "value": "Root", "level": 0 }, { "id": "n2", "value": "A", "level": 1 } ],
  "edges": [ { "from": "n1", "to": "n2" } ],
  "metadata": { "tree_type": "OBIR-Tree" }
}
```

### 6. 检索结果数据（query_results.json，可选）
- **由谁生成/消费**：C++生成，前端消费（如未生成则用mock数据）
- **作用/用途**：C++可直接写入top-k空间文本检索结果，前端展示
- **字段说明**：
  | 字段名      | 类型   | 含义           | 示例         |
  |-------------|--------|----------------|--------------|
  | title       | string | 结果标题       | "北京大学本部" |
  | description | string | 结果描述       | "北京市海淀区..." |
  | relevance   | int    | 相关性得分     | 95           |
  | location    | string | 位置描述       | "北京市..."   |
  | distance    | float  | 距离(单位km)   | 0.2          |
  | type        | string | 类型           | "教育机构"    |
- **示例**：
```json
[
  {
    "title": "北京大学本部",
    "description": "北京市海淀区颐和园路5号",
    "relevance": 95,
    "location": "北京市海淀区",
    "distance": 0.2,
    "type": "教育机构"
  }
]
```

---

## 典型流程举例

1. **前端发起检索**：
   - 前端POST `/api/query-results`，写入`search_query.json`。
2. **C++监听到search_query.json变化**：
   - 解析检索参数，生成/更新`ir_tree_data.json`、`ir_obir_mapping.json`、`ir_obir_annotations.json`、`ir_logic_path_data.json`、`obir_tree_current.json`、`obir_tree_previous.json`等。
   - 可选：写入`query_results.json`。
3. **前端刷新流程节点/实时路径**：
   - 前端自动请求各API，Python读取C++生成的数据文件，生成SVG并返回前端。
4. **前端展示最新SVG/检索结果**。

---

## C++后端开发注意事项

1. **所有数据文件需写入`OBIR-Tree-Web/backend/data/`目录下**，文件名需与前端/后端约定一致。
2. **JSON格式需严格遵循示例**，避免字段缺失或类型错误。
3. **每次前端搜索后，C++应尽快根据`search_query.json`生成/更新所有相关数据文件**，以保证前端刷新时能获取到最新内容。
4. **如需扩展其它数据交互，可参考上述模式，前端/后端均易于扩展。**
5. **建议C++端监听文件变化或定时轮询`search_query.json`，实现准实时响应。**
6. **如有字段含义不明或需扩展，请与前端/后端开发沟通确认。**

---

如有更多接口需求或格式变更，请及时与前端/后端开发协商！
