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
            <el-col :span="7">
                <el-card shadow="hover" :body-style="{ height: '380px' }">
                    <div class="card-header">
                        <p class="card-header-title">时间线</p>
                        <p class="card-header-desc">项目进度记录</p>
                    </div>
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
                </el-card>
            </el-col>
            <el-col :span="10">
                <el-card shadow="hover" :body-style="{ height: '380px' }" class="map-card-clickable" @click="goToMap">
                    <div class="card-header">
                        <p class="card-header-title">地域分布</p>
                        <p class="card-header-desc">数据地域分布情况</p>
                    </div>
                    <div class="map-chart-center">
                        <v-chart v-if="mapReady" ref="mapChart" class="map-chart-large" :option="mapOptions" />
                    </div>
                </el-card>
            </el-col>
            <el-col :span="7">
                <el-card shadow="hover" :body-style="{ height: '380px' }">
                    <div class="card-header">
                        <p class="card-header-title">检索排行</p>
                        <p class="card-header-desc">被检索次数排行Top5</p>
                    </div>
                    <!-- <div>
                        <div class="rank-item" v-for="(rank, index) in ranks">
                            <div class="rank-item-avatar">{{ index + 1 }}</div>
                            <div class="rank-item-content">
                                <div class="rank-item-top">
                                    <div class="rank-item-title">{{ rank.title }}</div>
                                    <div class="rank-item-desc">销量：{{ rank.value }}</div>
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
                    </div> -->
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

onMounted(async () => {
    // 1. 先注册地图
    const mapLoaded = await loadWorldMap();
    if (!mapLoaded) {
        // 地图没加载出来，直接return，页面不渲染地图
        return;
    }
    // 2. 先加载旧的country_count.json
    let countryCount = {};
    try {
        const res = await fetch('/mock/country_count.json');
        if (res.ok) {
            const text = await res.text();
            if (text.trim()) {
                countryCount = JSON.parse(text);
            }
        }
    } catch (e) {
        countryCount = {};
    }
    mapData.value = Object.entries(countryCount).map(([name, value]) => ({ name, value }));
    mapOptions.series[0].data = mapData.value;
    mapReady.value = true;

    // 3. 后台异步请求生成新数据，完成后再刷新
    fetch('/mock/gen_country_count').then(async () => {
        try {
            const res2 = await fetch('/mock/country_count.json?_t=' + Date.now());
            if (res2.ok) {
                const text2 = await res2.text();
                if (text2.trim()) {
                    const countryCount2 = JSON.parse(text2);
                    mapData.value = Object.entries(countryCount2).map(([name, value]) => ({ name, value }));
                    mapOptions.series[0].data = mapData.value;
                }
            }
        } catch (e) {}
    });
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
        description: '检索功能设计中',
        timestamp: '30分钟前',
        color: '#00bcd4',
    },
    {
        content: '地图测试',
        description: '地图数据显示功能正常,可以使用',
        timestamp: '15天前',
        color: '#1ABC9C',
    },
    {
        content: '测试数据上传',
        description: '测试数据上传成功,数据量10000条',
        timestamp: '19天前',
        color: '#3f51b5',
    },
    {
        content: '数据库连接',
        description: '数据库连接成功,调试正常',
        timestamp: '21天前',
        color: '#f44336',
    },
    {
        content: '页面上线',
        description: '数据管理页面与数据库页面上线',
        timestamp: '31天前',
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
const goToMap = () => {
    router.push('/project-search/map');
};
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
/* .map-chart {
    width: 100%;
    height: 350px;
} */
.map-chart-center {
    width: 600px;
    height: 600px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto;
    transform: translate(-60px, -140px);
}
.map-chart-large {
    width: 600px;
    height: 600px;
}
.map-card-clickable {
    cursor: pointer;
}
</style> 