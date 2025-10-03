# OBIR-Tree实时路径展示 - C++集成指南

## 概述

OBIR-Tree实时路径展示功能允许实时监控OBIR-Tree结构的变化，包括节点的新增、删除和修改。系统采用前后端分离架构，C++代码负责生成树结构数据，Python脚本负责生成SVG可视化，前端负责展示和交互。

## 系统架构

```
C++后端 → JSON数据文件 → Python脚本 → SVG图像 → 前端展示
```

## 数据格式规范

### 1. 当前树结构数据 (obir_tree_current.json)

```json
{
  "nodes": [
    {
      "id": "node_id",
      "value": "节点显示值",
      "level": 0,
      "status": "active"
    }
  ],
  "edges": [
    {
      "from": "parent_node_id",
      "to": "child_node_id"
    }
  ],
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0",
    "description": "当前时刻的OBIR-Tree结构"
  }
}
```

### 2. 前一时刻树结构数据 (obir_tree_previous.json)

格式与当前数据相同，用于计算差异。

## C++代码集成步骤

### 步骤1: 创建数据输出函数

```cpp
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct TreeNode {
    std::string id;
    std::string value;
    int level;
    std::string status;
};

struct TreeEdge {
    std::string from;
    std::string to;
};

struct TreeData {
    std::vector<TreeNode> nodes;
    std::vector<TreeEdge> edges;
    std::string timestamp;
    std::string version;
    std::string description;
};

void saveTreeData(const TreeData& data, const std::string& filename) {
    json j;
    
    // 转换节点数据
    json nodes = json::array();
    for (const auto& node : data.nodes) {
        json nodeJson;
        nodeJson["id"] = node.id;
        nodeJson["value"] = node.value;
        nodeJson["level"] = node.level;
        nodeJson["status"] = node.status;
        nodes.push_back(nodeJson);
    }
    j["nodes"] = nodes;
    
    // 转换边数据
    json edges = json::array();
    for (const auto& edge : data.edges) {
        json edgeJson;
        edgeJson["from"] = edge.from;
        edgeJson["to"] = edge.to;
        edges.push_back(edgeJson);
    }
    j["edges"] = edges;
    
    // 添加元数据
    j["metadata"]["timestamp"] = data.timestamp;
    j["metadata"]["version"] = data.version;
    j["metadata"]["description"] = data.description;
    
    // 写入文件
    std::ofstream file(filename);
    file << j.dump(2);
}
```

### 步骤2: 实现树结构更新逻辑

```cpp
class OBIRTreeManager {
private:
    TreeData currentData;
    TreeData previousData;
    std::string dataDir;
    
public:
    OBIRTreeManager(const std::string& dir) : dataDir(dir) {}
    
    // 更新树结构
    void updateTree(const TreeData& newData) {
        // 保存前一时刻数据
        if (!currentData.nodes.empty()) {
            previousData = currentData;
            saveTreeData(previousData, dataDir + "/obir_tree_previous.json");
        }
        
        // 更新当前数据
        currentData = newData;
        saveTreeData(currentData, dataDir + "/obir_tree_current.json");
    }
    
    // 添加节点
    void addNode(const TreeNode& node) {
        currentData.nodes.push_back(node);
    }
    
    // 删除节点
    void removeNode(const std::string& nodeId) {
        auto it = std::find_if(currentData.nodes.begin(), currentData.nodes.end(),
            [&nodeId](const TreeNode& node) { return node.id == nodeId; });
        if (it != currentData.nodes.end()) {
            currentData.nodes.erase(it);
        }
    }
    
    // 修改节点
    void modifyNode(const std::string& nodeId, const std::string& newValue) {
        for (auto& node : currentData.nodes) {
            if (node.id == nodeId) {
                node.value = newValue;
                break;
            }
        }
    }
    
    // 添加边
    void addEdge(const TreeEdge& edge) {
        currentData.edges.push_back(edge);
    }
    
    // 保存当前状态
    void saveCurrentState() {
        saveTreeData(currentData, dataDir + "/obir_tree_current.json");
    }
};
```

### 步骤3: 集成到主程序

```cpp
int main() {
    // 初始化树管理器
    OBIRTreeManager treeManager("./data");
    
    // 创建初始树结构
    TreeData initialData;
    initialData.timestamp = getCurrentTimestamp();
    initialData.version = "1.0";
    initialData.description = "初始OBIR-Tree结构";
    
    // 添加根节点
    TreeNode root;
    root.id = "root";
    root.value = "Root";
    root.level = 0;
    root.status = "active";
    initialData.nodes.push_back(root);
    
    // 保存初始数据
    treeManager.updateTree(initialData);
    
    // 模拟实时更新
    while (true) {
        // 执行OBIR-Tree操作...
        
        // 添加新节点
        TreeNode newNode;
        newNode.id = "node_" + std::to_string(getCurrentTime());
        newNode.value = "NewNode";
        newNode.level = 1;
        newNode.status = "active";
        treeManager.addNode(newNode);
        
        // 添加边
        TreeEdge newEdge;
        newEdge.from = "root";
        newEdge.to = newNode.id;
        treeManager.addEdge(newEdge);
        
        // 保存当前状态
        treeManager.saveCurrentState();
        
        // 等待一段时间
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
    
    return 0;
}
```

## API接口说明

### 前端调用接口

```javascript
// 获取OBIR-Tree实时数据
const response = await fetch('/api/obir-tree-realtime', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        currentFile: 'obir_tree_current.json',
        previousFile: 'obir_tree_previous.json'
    })
});

const result = await response.json();
if (result.success) {
    console.log('SVG内容:', result.svg);
    console.log('差异信息:', result.differences);
    console.log('当前节点数:', result.current_nodes);
    console.log('前一时刻节点数:', result.previous_nodes);
}
```

### 返回数据格式

```json
{
  "success": true,
  "svg": "<svg>...</svg>",
  "differences": {
    "added": ["node1", "node2"],
    "removed": ["old_node"],
    "modified": ["updated_node"]
  },
  "current_nodes": 10,
  "previous_nodes": 8
}
```

## 文件结构

```
backend/
├── data/
│   ├── obir_tree_current.json    # 当前树结构数据
│   └── obir_tree_previous.json   # 前一时刻树结构数据
├── gen_OBIR_Tree_realtime_svg.py # SVG生成脚本
└── app.py                        # Flask API服务器
```

## 部署说明

### 1. 启动后端服务

```bash
cd OBIR-Tree-Web/backend
python3 app.py
```

### 2. 启动前端服务

```bash
cd OBIR-Tree-Web
npm run dev
```

### 3. 访问页面

打开浏览器访问 `http://localhost:5174/#/obir-tree-realtime`

## 实时更新机制

1. **C++代码**：定期更新 `obir_tree_current.json` 文件
2. **Python脚本**：读取当前和前一时刻数据，计算差异
3. **前端组件**：支持自动刷新（默认5秒间隔）
4. **差异显示**：
   - 绿色发光：新增节点
   - 橙色：修改节点
   - 红色半透明：删除节点

## 注意事项

1. **文件权限**：确保C++代码有权限写入数据文件
2. **数据格式**：严格遵循JSON格式规范
3. **时间戳**：建议使用ISO 8601格式
4. **错误处理**：C++代码应包含适当的错误处理机制
5. **性能优化**：对于大型树结构，考虑增量更新策略

## 扩展功能

1. **WebSocket支持**：实现真正的实时推送
2. **历史记录**：保存多个历史版本
3. **节点详情**：点击节点显示详细信息
4. **动画效果**：添加节点变化动画
5. **导出功能**：支持导出SVG或PNG格式 