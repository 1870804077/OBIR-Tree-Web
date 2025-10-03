<template>
    <div>
        <el-row :gutter="20" class="mgb20">
            <el-col :span="6">
                <el-card shadow="hover" body-class="card-body">
                    <el-icon class="card-icon bg1">
                        <Search />
                    </el-icon>
                    <div class="card-content">
                        <countup class="card-num color1" :end="searchCount" />
                        <div>累计搜索次数</div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" body-class="card-body">
                    <el-icon class="card-icon bg2">
                        <DataLine />
                    </el-icon>
                    <div class="card-content">
                        <countup class="card-num color2" :end="dataAmount" />
                        <div>数据量</div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" body-class="card-body">
                    <el-icon class="card-icon bg3">
                        <FolderOpened />
                    </el-icon>
                    <div class="card-content">
                        <countup class="card-num color3" :end="spaceUsage" />
                        <div>OBIR-Tree占用空间(GB)</div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" body-class="card-body">
                    <el-icon class="card-icon bg4">
                        <Timer />
                    </el-icon>
                    <div class="card-content">
                        <countup class="card-num color4" :end="avgSearchTime" />
                        <div>平均搜索耗时(ms)</div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
        <el-row :gutter="20">
            <el-col :span="8">
                <el-card shadow="hover" :body-style="{ height: '380px', padding: '10px' }" class="data-card">
                    <div class="card-header">
                        <p class="card-header-title">时间线</p>
                        <p class="card-header-desc">项目进度记录</p>
                    </div>
                    <div class="card-content-container">
                        <el-timeline>
                            <el-timeline-item v-for="(activity, index) in activities" :key="index" :color="activity.color">
                                <div class="timeline-item">
                                    <div>
                                        <p>{{ activity.content }}</p>
                                        <p class="timeline-desc">{{ activity.description }}</p>
                                    </div>
                                    <div class="timeline-time">{{ activity.timestamp }}</div>
                                </div>
                            </el-timeline-item>
                        </el-timeline>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="8">
                <el-card shadow="hover" :body-style="{ height: '380px', padding: '10px' }" class="data-card map-card-clickable">
                    <div class="card-header">
                        <p class="card-header-title">地域分布</p>
                        <p class="card-header-desc">数据地域分布情况</p>
                    </div>
                    <div class="card-content-container">
                        <div class="map-chart-container">
                            <v-chart v-if="mapReady" ref="mapChart" class="vue-manage-system-map" :option="mapOptions" />
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="8">
                <el-card shadow="hover" :body-style="{ height: '380px', padding: '10px' }" class="data-card">
                    <div class="card-header">
                        <p class="card-header-title">检索排行</p>
                        <p class="card-header-desc">数据项被检索次数排行Top5</p>
                    </div>
                    <div class="card-content-container">
                        <div class="rank-item" v-for="(rank, index) in ranks">
                            <div class="rank-item-avatar">{{ index + 1 }}</div>
                            <div class="rank-item-content">
                                <div class="rank-item-top">
                                    <div class="rank-item-title">{{ rank.title }}</div>
                                    <div class="rank-item-desc">被检索次数：{{ rank.value }}</div>
                                </div>
                                <el-progress
                                    :show-text="false"
                                    striped
                                    :stroke-width="10"
                                    :percentage="rank.percent"
                                    :color="rank.color"
                                />
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts" name="DataOverview">
import countup from '@/components/countup.vue';
import { ref, onMounted, onActivated, nextTick } from 'vue';
import { Search, DataLine, FolderOpened, Timer } from '@element-plus/icons-vue';
import VChart from 'vue-echarts';
import { mapOptions } from './chart/options';
// ECharts 注册，防止 Renderer 'undefined' 报错
import { use, registerMap } from 'echarts/core';
import { BarChart, LineChart, PieChart, MapChart } from 'echarts/charts';
import {
    GridComponent,
    TooltipComponent,
    LegendComponent,
    TitleComponent,
    VisualMapComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import chinaMap from '@/utils/china';
import { useRouter } from 'vue-router';
use([
    CanvasRenderer,
    BarChart,
    GridComponent,
    LineChart,
    PieChart,
    TooltipComponent,
    LegendComponent,
    TitleComponent,
    VisualMapComponent,
    MapChart,
]);

const mapReady = ref(false);
const mapData = ref([]);
const mapChart = ref();
function resizeMapChart() {
    nextTick(() => {
        if (mapChart.value && mapChart.value.resize) {
            mapChart.value.resize();
        }
    });
}

const loadWorldMap = async () => {
    try {
        const res = await fetch('/world.json');
        if (!res.ok) throw new Error('world.json not found');
        const worldMap = await res.json();
        registerMap('world', worldMap);
        return true;
    } catch (e) {
        console.error('加载 world.json 失败:', e);
        return false;
    }
};

const loadChinaMap = async () => {
    try {
        // 使用内置的中国地图数据
        registerMap('china', chinaMap);
        return true;
    } catch (e) {
        console.error('加载中国地图失败:', e);
        return false;
    }
};

// 数据转换函数 - 将国家数据转换为中国省份数据
const convertToProvinceData = (countryCount: Record<string, number>) => {
    const provinceData = [];
    
    // 处理中国省份数据 - 现在country_count.json中已经是中文名称了
    for (const [name, value] of Object.entries(countryCount)) {
        provinceData.push({
            name: name,
            value: value
        });
    }
    
    // 如果没有数据，添加一些默认值用于显示
    if (provinceData.length === 0) {
        provinceData.push(
            { name: '北京', value: 100 },
            { name: '上海', value: 80 },
            { name: '广东', value: 120 },
            { name: '江苏', value: 90 }
        );
    }
    
    return provinceData;
};
onMounted(async () => {
    // 1. 先注册地图
    const mapLoaded = await loadChinaMap();
    if (!mapLoaded) {
        // 地图没加载出来，直接return，页面不渲染地图
        return;
    }
    // 2. 先加载旧的country_count.json
    let countryCount = {};
    try {
        // 已禁用：/mock/country_count.json
        console.warn('[DataOverview] 初始统计数据暂不可用：请接入真实后端 API 替换原 /mock/country_count.json');
        countryCount = {};
    } catch (e) {
        countryCount = {};
    }
    
    // 转换数据格式为中国省份数据
    const provinceData = convertToProvinceData(countryCount);
    
    mapData.value = provinceData;
    mapOptions.series[0].data = mapData.value;
    mapReady.value = true;
    
    // 3. 后台异步请求生成新数据，完成后再刷新
    // 已禁用：/mock/gen_country_count 触发与刷新逻辑
    console.warn('[DataOverview] 异步统计刷新暂不可用：请接入真实后端 API 替换 /mock/gen_country_count 与 /mock/country_count.json');
});
onActivated(() => {
    resizeMapChart();
});
// 预留接口，后续可用API获取
const searchCount = ref(0); // 累计搜索次数
const dataAmount = ref(0); // 数据量
const spaceUsage = ref(0); // OBIR-Tree占用空间(GB)
const avgSearchTime = ref(0); // 平均搜索耗时(ms)
const activities = [
    {
        content: '最新进度',
        description: '前后端连接调试中',
        timestamp: '30分钟前',
        color: '#00bcd4',
    },
    {
        content: '检索流程图',
        description: '流程图框架搭建完毕,内部信息设计中',
        timestamp: '2天前',
        color: '#00bcd4',
    },
    {
        content: '地图测试',
        description: '地图数据显示功能正常,可以使用',
        timestamp: '7天前',
        color: '#1ABC9C',
    },
    {
        content: '测试数据上传',
        description: '测试数据上传成功,数据量10000条',
        timestamp: '11天前',
        color: '#3f51b5',
    },
    {
        content: '数据库连接',
        description: '数据库连接成功,调试正常',
        timestamp: '15天前',
        color: '#f44336',
    },
    {
        content: '页面初步搭建',
        description: '数据管理页面与数据库页面初步框架搭建',
        timestamp: '21天前',
        color: '#009688',
    },
];
const ranks = [
    {
        title: '手机',
        value: 10000,
        percent: 80,
        color: '#f25e43',
    },
    {
        title: '电脑',
        value: 8000,
        percent: 70,
        color: '#00bcd4',
    },
    {
        title: '相机',
        value: 6000,
        percent: 60,
        color: '#64d572',
    },
    {
        title: '衣服',
        value: 5000,
        percent: 55,
        color: '#e9a745',
    },
    {
        title: '书籍',
        value: 4000,
        percent: 50,
        color: '#009688',
    },
];
const router = useRouter();
// const goToMap = () => {
//     router.push('/project-search/map');
// };
</script>

<style>
.card-body {
    display: flex;
    align-items: center;
    height: 80px;
    padding: 0;
}
</style>
<style scoped>
.data-overview-container {
    padding: 0;
    min-height: calc(100vh - 120px);
    display: flex;
    flex-direction: column;
}

.mgb20 {
    margin-bottom: 20px;
}

.stats-row {
    flex-shrink: 0;
}

.content-row {
    flex: 1;
    margin-bottom: 0;
}

.card-content {
    flex: 1;
    text-align: center;
    font-size: 14px;
    color: #999;
    padding: 0 20px;
}

.card-num {
    font-size: 30px;
}

.card-icon {
    font-size: 50px;
    width: 100px;
    height: 100px;
    text-align: center;
    line-height: 100px;
    color: #fff;
}

.bg1 {
    background: #2d8cf0;
}

.bg2 {
    background: #64d572;
}

.bg3 {
    background: #f25e43;
}

.bg4 {
    background: #e9a745;
}

.color1 {
    color: #2d8cf0;
}

.color2 {
    color: #64d572;
}

.color3 {
    color: #f25e43;
}

.color4 {
    color: #e9a745;
}

.chart {
    width: 100%;
    height: 400px;
}

.card-header {
    padding-left: 10px;
    margin-bottom: 20px;
}

.card-header-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 5px;
}

.card-header-desc {
    font-size: 14px;
    color: #999;
}

.timeline-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 16px;
    color: #000;
}

.timeline-time,
.timeline-desc {
    font-size: 12px;
    color: #787878;
}

.rank-item {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.rank-item-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #f2f2f2;
    text-align: center;
    line-height: 40px;
    margin-right: 10px;
}

.rank-item-content {
    flex: 1;
}

.rank-item-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #343434;
    margin-bottom: 10px;
}

.rank-item-desc {
    font-size: 14px;
    color: #999;
}
.map-chart-container {
    width: 100%;
    height: 300px;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0;
}

.vue-manage-system-map {
    width: 90%;
    height: 90%;
    margin: auto;
}

.map-card-clickable {
    cursor: pointer;
    transition: all 0.3s ease;
}

.map-card-clickable:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    transform: translateY(-2px);
}

/* 移除旧的样式 */
.map-chart-center,
.map-chart-large {
    display: none;
}

/* 添加新的样式确保卡片一致性 */
.data-card {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.responsive-card {
    height: auto;
    min-height: 380px;
}

.responsive-card .el-card__body {
    height: auto;
    min-height: 360px;
    padding: 10px;
    display: flex;
    flex-direction: column;
}

.card-content-container {
    flex: 1;
    overflow: auto;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    min-height: 280px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .stats-row .el-col {
        margin-bottom: 10px;
    }
    
    .content-row .el-col {
        margin-bottom: 20px;
    }
    
    .responsive-card {
        min-height: 300px;
    }
    
    .responsive-card .el-card__body {
        min-height: 280px;
    }
    
    .card-content-container {
        min-height: 200px;
    }
    
    .vue-manage-system-map {
        min-height: 200px;
    }
    
    .map-chart-container {
        min-height: 200px;
        height: 200px;
    }
    
    .card-num {
        font-size: 24px;
    }
    
    .card-icon {
        font-size: 40px;
        width: 80px;
        height: 80px;
        line-height: 80px;
    }
}

@media (min-width: 1200px) {
    .data-overview-container {
        min-height: calc(100vh - 100px);
    }
    
    .responsive-card {
        min-height: 450px;
    }
    
    .responsive-card .el-card__body {
        min-height: 430px;
    }
    
    .card-content-container {
        min-height: 350px;
    }
    
    .vue-manage-system-map {
        min-height: 350px;
    }
    
    .map-chart-container {
        min-height: 350px;
        height: 350px;
    }
}
</style>