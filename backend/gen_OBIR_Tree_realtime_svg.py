#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OBIR-Tree实时路径展示SVG生成器
支持横向绘制OBIR-Tree结构，并标注前后差异
"""

import json
import os
from typing import Dict, List, Tuple, Optional

class OBIRTreeRealtimeSVGGenerator:
    def __init__(self):
        self.node_width = 120
        self.node_height = 60
        self.level_height = 100
        self.node_margin = 20
        
    def generate_from_files(self, current_data_file: str, previous_data_file: str = None) -> Dict:
        """
        从文件生成OBIR-Tree实时SVG
        
        Args:
            current_data_file: 当前树结构数据文件路径
            previous_data_file: 前一时刻树结构数据文件路径（可选）
            
        Returns:
            包含SVG内容和差异信息的字典
        """
        try:
            # 读取当前数据
            with open(current_data_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # 读取前一时刻数据（如果存在）
            previous_data = None
            if previous_data_file and os.path.exists(previous_data_file):
                with open(previous_data_file, 'r', encoding='utf-8') as f:
                    previous_data = json.load(f)
            
            # 计算差异
            differences = self._calculate_differences(current_data, previous_data)
            
            # 生成SVG
            svg_content = self._generate_svg(current_data, differences)
            
            return {
                'success': True,
                'svg': svg_content,
                'differences': differences,
                'current_nodes': len(current_data.get('nodes', [])),
                'previous_nodes': len(previous_data.get('nodes', [])) if previous_data else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_differences(self, current_data: Dict, previous_data: Optional[Dict]) -> Dict:
        """计算树结构差异"""
        if not previous_data:
            return {
                'added': [],
                'removed': [],
                'modified': []
            }
        
        current_nodes = {node['id']: node for node in current_data.get('nodes', [])}
        previous_nodes = {node['id']: node for node in previous_data.get('nodes', [])}
        
        added = []
        removed = []
        modified = []
        
        # 找出新增的节点
        for node_id, node in current_nodes.items():
            if node_id not in previous_nodes:
                added.append(node_id)
        
        # 找出删除的节点
        for node_id, node in previous_nodes.items():
            if node_id not in current_nodes:
                removed.append(node_id)
        
        # 找出修改的节点
        for node_id in current_nodes:
            if node_id in previous_nodes:
                current_node = current_nodes[node_id]
                previous_node = previous_nodes[node_id]
                if (current_node.get('value') != previous_node.get('value') or
                    current_node.get('status') != previous_node.get('status')):
                    modified.append(node_id)
        
        return {
            'added': added,
            'removed': removed,
            'modified': modified
        }
    
    def _generate_svg(self, data: Dict, differences: Dict) -> str:
        """生成OBIR-Tree的SVG"""
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        if not nodes:
            return '<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><text x="200" y="100" text-anchor="middle" fill="#666">暂无数据</text></svg>'
        
        # 计算布局
        layout = self._calculate_layout(nodes, edges)
        
        # 计算SVG尺寸
        max_x = max(layout[node_id]['x'] for node_id in layout) + self.node_width
        max_y = max(layout[node_id]['y'] for node_id in layout) + self.node_height
        width = max_x + 50
        height = max_y + 50
        
        # 生成SVG内容
        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
            '  <defs>',
            '    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">',
            '      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>',
            '      <feMerge>',
            '        <feMergeNode in="coloredBlur"/>',
            '        <feMergeNode in="SourceGraphic"/>',
            '      </feMerge>',
            '    </filter>',
            '  </defs>',
            '  <style>',
            '    .node { fill: #4CAF50; stroke: #2E7D32; stroke-width: 2; }',
            '    .node-added { fill: #4CAF50; stroke: #2E7D32; stroke-width: 3; filter: url(#glow); }',
            '    .node-removed { fill: #F44336; stroke: #D32F2F; stroke-width: 2; opacity: 0.6; }',
            '    .node-modified { fill: #FF9800; stroke: #F57C00; stroke-width: 3; }',
            '    .edge { stroke: #666; stroke-width: 2; fill: none; }',
            '    .text { fill: white; font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; }',
            '    .legend { fill: #333; font-family: Arial, sans-serif; font-size: 14px; }',
            '  </style>'
        ]
        
        # 绘制边
        for edge in edges:
            start_node = layout.get(edge['from'])
            end_node = layout.get(edge['to'])
            if start_node and end_node:
                x1 = start_node['x'] + self.node_width
                y1 = start_node['y'] + self.node_height // 2
                x2 = end_node['x']
                y2 = end_node['y'] + self.node_height // 2
                
                # 创建曲线路径
                control_x = (x1 + x2) // 2
                path = f'M {x1} {y1} Q {control_x} {y1} {x2} {y2}'
                svg_parts.append(f'    <path d="{path}" class="edge"/>')
        
        # 绘制节点
        for node in nodes:
            node_id = node['id']
            pos = layout[node_id]
            x = pos['x']
            y = pos['y']
            
            # 确定节点样式
            node_class = 'node'
            if node_id in differences['added']:
                node_class = 'node-added'
            elif node_id in differences['removed']:
                node_class = 'node-removed'
            elif node_id in differences['modified']:
                node_class = 'node-modified'
            
            # 绘制节点矩形
            svg_parts.append(f'    <rect x="{x}" y="{y}" width="{self.node_width}" height="{self.node_height}" rx="8" class="{node_class}"/>')
            
            # 绘制节点文本
            text_x = x + self.node_width // 2
            text_y = y + self.node_height // 2 + 4
            svg_parts.append(f'    <text x="{text_x}" y="{text_y}" class="text">{node.get("value", node_id)}</text>')
        
        # 绘制图例
        legend_y = height - 30
        legend_items = [
            ('正常节点', '#4CAF50', 10),
            ('新增节点', '#4CAF50', 110),
            ('修改节点', '#FF9800', 210),
            ('删除节点', '#F44336', 310)
        ]
        
        for text, color, x in legend_items:
            svg_parts.append(f'    <rect x="{x}" y="{legend_y}" width="15" height="15" fill="{color}" rx="3"/>')
            svg_parts.append(f'    <text x="{x + 20}" y="{legend_y + 12}" class="legend">{text}</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _calculate_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """计算节点布局（横向）"""
        layout = {}
        
        # 按层级分组节点
        levels = {}
        for node in nodes:
            level = node.get('level', 0)
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
        
        # 计算每个节点的位置
        for level in sorted(levels.keys()):
            level_nodes = levels[level]
            y = level * self.level_height + 50
            
            # 计算该层级节点的水平分布
            total_width = len(level_nodes) * (self.node_width + self.node_margin) - self.node_margin
            start_x = 50
            
            for i, node in enumerate(level_nodes):
                x = start_x + i * (self.node_width + self.node_margin)
                layout[node['id']] = {'x': x, 'y': y}
        
        return layout

def generate_svg(current_data_file: str, previous_data_file: str = None) -> str:
    """便捷函数：生成OBIR-Tree实时SVG"""
    generator = OBIRTreeRealtimeSVGGenerator()
    result = generator.generate_from_files(current_data_file, previous_data_file)
    return result.get('svg', '') if result['success'] else ''

if __name__ == "__main__":
    # 测试代码
    current_file = "data/obir_tree_current.json"
    previous_file = "data/obir_tree_previous.json"
    
    generator = OBIRTreeRealtimeSVGGenerator()
    result = generator.generate_from_files(current_file, previous_file)
    
    if result['success']:
        print("SVG生成成功")
        print(f"当前节点数: {result['current_nodes']}")
        print(f"前一时刻节点数: {result['previous_nodes']}")
        print(f"新增节点: {len(result['differences']['added'])}")
        print(f"删除节点: {len(result['differences']['removed'])}")
        print(f"修改节点: {len(result['differences']['modified'])}")
    else:
        print(f"生成失败: {result['error']}") 