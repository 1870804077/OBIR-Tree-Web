<template>
	<div>
		<!-- /*这里的总条数是自己输入的，这里记得最后要改*/ -->
		<div class="container">
			<TableCustom :columns="columns" :tableData="tableData" :total="1000" :viewFunc="handleViewSimple"
				:editFunc="handleEdit" :refresh="getData" :currentPage="page.index"
				:pageSize="page.size" :changePage="changePage">
				<template #toolbarBtn>
					<!-- <el-button type="warning" :icon="CirclePlusFilled" @click="visible = true">新增</el-button> -->
					<el-button type="primary" @click="showAllOnMap">在地图上显示</el-button>
					<el-input v-model="query.value" placeholder="文本内容" style="width: 200px; margin-left: 10px;" />
					<el-button type="success" @click="handleSearch" style="margin-left: 10px;">搜索</el-button>
				</template>
				<template #coordinates="{ rows }">
					({{ rows.longitude }}, {{ rows.latitude }})
				</template>
				<template #encrypted_data="{ rows }">
					<div>
						<span v-if="rows.has_encrypted_data">{{ rows.encrypted_data.slice(0,30)}}</span>
						<span v-else style="color: #aaa;">无加密数据</span>
					</div>
				</template>
			</TableCustom>

		</div>
		<!-- 搜索结果弹窗 -->
		<el-dialog title="搜索结果" v-model="searchVisible" width="1000px" destroy-on-close>
			<el-table :data="searchResults" border>
				<el-table-column prop="value" label="文本内容" />
				<el-table-column label="坐标" >
					<template #default="scope">({{ scope.row.longitude }}, {{ scope.row.latitude }})</template>
				</el-table-column>
				<el-table-column prop="encrypted_data" label="加密数据(前30位)" />
			</el-table>
		</el-dialog>
		<el-dialog :title="isEdit ? '编辑' : '新增'" v-model="visible" width="700px" destroy-on-close
			:close-on-click-modal="false" @close="closeDialog">
			<TableEdit :form-data="rowData" :options="options" :edit="isEdit" :update="updateData">
			</TableEdit>
		</el-dialog>
		<el-dialog title="查看详情" v-model="visible1" width="700px" destroy-on-close>
			<TableDetail :data="viewData">
			</TableDetail>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="basetable">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElInput, ElButton, ElDialog, ElTable, ElTableColumn } from 'element-plus';
import { CirclePlusFilled } from '@element-plus/icons-vue';
import request from '@/utils/request';
import TableCustom from '@/components/table-custom.vue';
import TableDetail from '@/components/table-detail.vue';
import { TableItem } from '@/types/table';
import { FormOption, FormOptionList } from '@/types/form-option';
import { useRouter } from 'vue-router';

const router = useRouter();

// 查询相关
const query = reactive({
	value: '',
});

// 搜索结果相关
const searchVisible = ref(false);
const searchResults = ref<TableItem[]>([]);
const handleSearch = async () => {
	if (!query.value.trim()) {
		ElMessage.warning('请输入搜索内容');
		return;
	}
	
	try {
		// 调用后端搜索API
		
		const response = await request.get('/search', {
			params: {
				keyword: query.value.trim()
			}
		});
		
		// 解析API返回结果
		if (response.data.status === 'success') {
			// 转换后端返回格式为前端需要的TableItem格式
			searchResults.value = response.data.results.map((item: any) => ({
				id: item.id,
				value: item.keyword,
				longitude: item.x,
				latitude: item.y,
				encrypted_data: generateMockData()[0].encrypted_data,
				has_encrypted_data: !!item.encrypted
			}));
			
			if (searchResults.value.length === 0) {
				ElMessage.info('未找到匹配的搜索结果');
			}
			searchVisible.value = true;
		} else {
			ElMessage.error('搜索失败：' + (response.data.message || '未知错误'));
		}
	} catch (error) {
		console.error('搜索请求出错：', error);
		ElMessage.error('搜索请求失败，请稍后重试');
	}
};

// 表格相关
let columns = ref([
	{ type: 'selection' },
	{ type: 'index', label: 'index', width: 55, align: 'center' },
	{ prop: 'value', label: 'value' },
	{ prop: 'coordinates', label: '坐标', slot: true },
	{ prop: 'encrypted_data', label: '加密数据(前30位)', slot: true },
	{ prop: 'operator', label: '操作', width: 100 },
])
const page = reactive({
	index: 1,
	size: 20,
	total: 0,
})
const tableData = ref<TableItem[]>([]);

const getData = async () => {
    try {
        // 使用data-range接口获取原始数据和加密数据
        const response = await request.get('/data-range', {
            params: {
                start: (page.index - 1) * page.size,
                end: page.index * page.size - 1
            }
        });
        if (response.data && response.data.data) {
            // 直接使用后端返回的结构
            tableData.value = response.data.data.map(item => ({
                ...item,
                value: item.keyword,
                longitude: item.x,
                latitude: item.y
            }));
            page.total = response.data.total_available || 0;
        } else {
            // 如果后端还没有实现该接口，使用模拟数据
            console.warn('后端接口未实现，使用模拟数据');
            tableData.value = generateMockData();
            page.total = 100;
        }
    } catch (e) {
        console.error('无法获取数据库数据，错误为', e);
        ElMessage.error('获取数据失败，使用模拟数据');
        // 使用模拟数据作为后备
        tableData.value = generateMockData();
        page.total = 100;
    }
};

// 修正模拟数据生成函数，确保包含加密数据且长度正确
const generateMockData = () => {
    const mockData = [];
    const startIndex = (page.index - 1) * page.size;
    for (let i = 0; i < page.size; i++) {
        const id = startIndex + i + 1;
        // 生成30位随机加密数据
        const array = new Uint8Array(15); // 15字节 = 120位 = 30个十六进制字符
        crypto.getRandomValues(array);
        const encryptedData = Array.from(array, byte => byte.toString(16).padStart(2, '0').toUpperCase()).join('');
        mockData.push({
            id: id,
            value: `数据项${id}`,
            longitude: 108.9 + Math.random() * 0.2,
            latitude: 34.2 + Math.random() * 0.2,
            encrypted_data: encryptedData,
            has_encrypted_data: true
        });
    }
    return mockData;
};

const changePage = (val: number) => {
	page.index = val;
	getData();
};

// 新增/编辑弹窗相关
let options = ref<FormOption>({
	labelWidth: '100px',
	span: 24,
	list: [
		{ type: 'input', label: '唯一标识码', prop: 'id', required: true },
		{ type: 'input', label: '文本内容', prop: 'value', required: true },
		{ type: 'number', label: '经度', prop: 'longitude', required: true },
		{ type: 'number', label: '纬度', prop: 'latitude', required: true },
	]
})
const visible = ref(false);
const isEdit = ref(false);
const rowData = ref({});
const handleEdit = (row: TableItem) => {
	rowData.value = { ...row };
	isEdit.value = true;
	visible.value = true;
};
const updateData = () => {
	closeDialog();
	getData();
};

const closeDialog = () => {
	visible.value = false;
	isEdit.value = false;
};

// 查看详情弹窗相关
const visible1 = ref(false);
const viewData = ref({
	row: {},
	list: []
});
const handleView = (row: TableItem) => {
  // 跳转到地图检索界面并显示该点
  router.push({
    path: '/project-search/map',
    query: {
      lng: row.longitude,
      lat: row.latitude
    }
  });
};

// 新增：简单查看方法，不显示区域圈
const handleViewSimple = (row: TableItem) => {
  // 跳转到地图检索界面并显示该点，但不显示区域圈
  router.push({
    path: '/project-search/map',
    query: {
      lng: row.longitude,
      lat: row.latitude,
      simple: 'true' // 添加标识，表示简单查看模式
    }
  });
};

// 删除相关
const handleDelete = (row: TableItem) => {
	ElMessage.success('删除成功');
}

const showAllOnMap = async () => {
  // 已禁用：历史演示的 mock points.json。保留跳转入口但不传点位。
  try {
    console.warn('[DatabaseView] points 显示暂不可用：请接入真实后端 API 替换原 /mock/points.json');
  } catch (e) {
    console.error('无法获取后端的返回结果，错误为', e);
  }
  router.push({
    path: '/project-search/map'
  });
};

onMounted(() => {
    getData();
});
</script>

<style scoped>
.container {
	padding: 30px;
	background-color: #fff;
	border-radius: 5px;
	border: 1px solid #ddd;
	width: 100%;
	box-sizing: border-box;
}

.table-td-thumb {
	display: block;
	margin: auto;
	width: 40px;
	height: 40px;
}

:deep(.el-dialog) {
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  margin: 0 !important;
}

</style>