# IR-Tree SVG 后端服务

## 功能说明

这个后端服务为前端提供IR-Tree SVG生成功能，从C++代码生成的数据文件中读取IR-Tree结构并生成SVG向量图。

## 文件结构

```
backend/
├── app.py                 # Flask API服务器
├── gen_IR_Tree_svg.py    # SVG生成器
├── requirements.txt       # Python依赖
├── data/                 # 数据文件目录
│   └── ir_tree_data.json # 示例数据文件
└── README.md             # 本文档
```

## 安装和运行

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动。

## API接口

### 生成IR-Tree SVG
- **URL**: `/api/ir-tree-svg`
- **方法**: `POST`
- **请求体**:
```json
{
  "dataFile": "ir_tree_data.json"
}
```
- **响应**:
```json
{
  "success": true,
  "svg": "<svg>...</svg>"
}
```

## 与C++代码协同工作

### 数据文件格式

C++代码需要生成以下JSON格式的数据文件：

```json
{
  "nodes": [
    {
      "id": "节点ID",
      "label": "节点标签",
      "type": "节点类型(root/node/leaf)",
      "level": 层级(0开始)
    }
  ],
  "edges": [
    {
      "from": "起始节点ID",
      "to": "目标节点ID"
    }
  ]
}
```

### C++代码集成步骤

1. **在C++代码中添加JSON输出功能**
```cpp
#include <nlohmann/json.hpp>
using json = nlohmann::json;

// 构建IR-Tree数据结构
json tree_data;
tree_data["nodes"] = json::array();
tree_data["edges"] = json::array();

// 添加节点
for (const auto& node : ir_tree_nodes) {
    json node_obj;
    node_obj["id"] = node.id;
    node_obj["label"] = node.label;
    node_obj["type"] = node.type;
    node_obj["level"] = node.level;
    tree_data["nodes"].push_back(node_obj);
}

// 添加边
for (const auto& edge : ir_tree_edges) {
    json edge_obj;
    edge_obj["from"] = edge.from_id;
    edge_obj["to"] = edge.to_id;
    tree_data["edges"].push_back(edge_obj);
}

// 写入文件
std::ofstream file("backend/data/ir_tree_data.json");
file << tree_data.dump(2);
```

2. **在C++代码执行后调用Python脚本**
```cpp
// 生成数据文件后，调用Python脚本生成SVG
system("cd backend && python gen_IR_Tree_svg.py data/ir_tree_data.json > ir_tree.svg");
```

3. **或者通过API接口**
```cpp
// 使用HTTP客户端库调用API
// 例如使用libcurl或cpp-httplib
```

### 数据文件位置

C++代码生成的数据文件应放在 `backend/data/` 目录下，前端会通过API接口读取这些文件。

### 节点类型说明

- `root`: 根节点（绿色）
- `node`: 中间节点（青色）
- `leaf`: 叶子节点（红色）

## 开发说明

### 添加新的节点类型

在 `gen_IR_Tree_svg.py` 的 `generate_svg` 方法中添加新的颜色映射：

```python
if node['type'] == 'new_type':
    fill_color = '#your_color'
```

### 自定义布局

修改 `calculate_layout` 方法中的布局参数：

```python
self.node_radius = 20      # 节点半径
self.level_height = 80     # 层级间距
self.node_spacing = 60     # 同级节点间距
```

## 测试

1. 确保后端服务器运行
2. 在浏览器中访问 `http://localhost:5000/api/health`
3. 点击第一个节点查看SVG显示效果 