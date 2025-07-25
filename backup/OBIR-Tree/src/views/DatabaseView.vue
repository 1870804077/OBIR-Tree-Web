<template>
	<div>
		<TableSearch :query="query" :options="searchOpt" :search="handleSearch" />
		<div class="container">
			<TableCustom :columns="columns" :tableData="tableData" :total="page.total" :viewFunc="handleView"
				:delFunc="handleDelete" :editFunc="handleEdit" :refresh="getData" :currentPage="page.index"
				:changePage="changePage">
				<template #toolbarBtn>
					<el-button type="warning" :icon="CirclePlusFilled" @click="visible = true">新增</el-button>
				</template>
				<template #coordinates="{ rows }">
					{{ rows.latitude }}, {{ rows.longitude }}
				</template>
			</TableCustom>

		</div>
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
import { ElMessage, } from 'element-plus';
import { CirclePlusFilled } from '@element-plus/icons-vue';
import { fetchData } from '@/api/index';
import TableCustom from '@/components/table-custom.vue';
import TableDetail from '@/components/table-detail.vue';
import TableSearch from '@/components/table-search.vue';
import { TableItem } from '@/types/table';
import { FormOption, FormOptionList } from '@/types/form-option';
import { useRouter } from 'vue-router';

const router = useRouter();

// 查询相关
const query = reactive({
	value: '',
});
const searchOpt = ref<FormOptionList[]>([
	{ type: 'input', label: '文本内容：', prop: 'value' }
])
const handleSearch = () => {
	changePage(1);
};

// 表格相关
let columns = ref([
	{ type: 'selection' },
	{ type: 'index', label: 'index', width: 55, align: 'center' },
	{ prop: 'value', label: 'value' },
	{ prop: 'latitude', label: '纬度' },
	{ prop: 'longitude', label: '经度' },
	{ prop: 'coordinates', label: '坐标', slot: true },
	{ prop: 'operator', label: '操作', width: 250 },
])
const page = reactive({
	index: 1,
	size: 20,
	total: 0,
})
const tableData = ref<TableItem[]>([]);

const getData = async () => {
    // 读取 public/mock/data.txt
    const res = await fetch('/mock/data.txt');
    const text = await res.text();
    const lines = text.trim().split('\n');
    page.total = lines.length;
    const start = (page.index - 1) * page.size;
    const end = start + page.size;
    const parsed = lines.slice(start, end).map(line => {
        const [id, value, latitude, longitude] = line.split(' ');
        return { id, value, latitude, longitude };
    });
    tableData.value = parsed;
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
		{ type: 'number', label: '纬度', prop: 'latitude', required: true },
		{ type: 'number', label: '经度', prop: 'longitude', required: true },
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
	// 跳转到地图检索界面并搜索坐标数据
	router.push({
		path: '/project-search/map',
		query: {
			latitude: row.latitude,
			longitude: row.longitude,
			value: row.value
		}
	});
};

// 删除相关
const handleDelete = (row: TableItem) => {
	ElMessage.success('删除成功');
}

onMounted(() => {
    getData();
});
</script>

<style scoped>
.table-td-thumb {
	display: block;
	margin: auto;
	width: 40px;
	height: 40px;
}
</style> 