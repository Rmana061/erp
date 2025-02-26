<!-- 操作紀錄 -->
<template>
  <body class="admin-mode">
    <div class="container">
      <button class="bookmark-toggle" @click="toggleSidebar">
        <span class="bookmark-text">選單</span>
      </button>
      <div class="sidebar-overlay" :class="{ active: isSidebarActive }" @click="closeSidebar"></div>
      <SideBar menu-type="admin" :class="{ active: isSidebarActive }" />
      <div class="main-content">
        <div class="header">
          <span>Hi {{ adminName }}您好,</span>
          <span>{{ currentTime }}</span>
        </div>
        <div class="content-wrapper">
          <div class="scrollable-content">
            <h2>操作紀錄查詢</h2>
            
            <!-- 查詢條件 -->
            <div class="search-container">
              <div class="search-row">
                <div class="search-item">
                  <label>表名：</label>
                  <select v-model="searchParams.table_name">
                    <option value="">全部</option>
                    <option value="orders">訂單</option>
                    <option value="customers">客戶</option>
                    <option value="products">產品</option>
                    <option value="administrators">管理員</option>
                  </select>
                </div>
                <div class="search-item">
                  <label>操作類型：</label>
                  <select v-model="searchParams.operation_type">
                    <option value="">全部</option>
                    <option value="新增">新增</option>
                    <option value="修改">修改</option>
                    <option value="刪除">刪除</option>
                    <option value="審核">審核</option>
                  </select>
                </div>
                <div class="search-item">
                  <label>用戶類型：</label>
                  <select v-model="searchParams.user_type">
                    <option value="">全部</option>
                    <option value="管理員">管理員</option>
                    <option value="客戶">客戶</option>
                  </select>
                </div>
              </div>
              <div class="search-row">
                <div class="search-item">
                  <label>開始日期：</label>
                  <input type="date" v-model="searchParams.start_date">
                </div>
                <div class="search-item">
                  <label>結束日期：</label>
                  <input type="date" v-model="searchParams.end_date">
                </div>
                <div class="search-item">
                  <button class="search-button" @click="searchLogs">查詢</button>
                </div>
              </div>
            </div>

            <!-- 日誌列表 -->
            <div class="table-container">
              <table class="log-list">
                <thead>
                  <tr>
                    <th>時間</th>
                    <th>用戶類型</th>
                    <th>操作者</th>
                    <th>表名</th>
                    <th>操作對象</th>
                    <th>操作類型</th>
                    <th>詳細資訊</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in logs" :key="log.id">
                    <td>{{ formatDateTime(log.created_at) }}</td>
                    <td>{{ log.user_type }}</td>
                    <td>{{ log.performer_name }}</td>
                    <td>{{ getTableDisplayName(log.table_name) }}</td>
                    <td>{{ getRecordDetail(log) }}</td>
                    <td>{{ log.operation_type }}</td>
                    <td>
                      <button class="detail-button" @click="showLogDetail(log)">
                        查看
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 分頁 -->
            <div class="pagination" v-if="totalPages > 1">
              <button 
                :disabled="currentPage === 1"
                @click="changePage(currentPage - 1)">
                上一頁
              </button>
              <span>{{ currentPage }} / {{ totalPages }}</span>
              <button 
                :disabled="currentPage === totalPages"
                @click="changePage(currentPage + 1)">
                下一頁
              </button>
            </div>

            <!-- 詳細資訊彈窗 -->
            <div class="modal" v-if="showModal">
              <div class="modal-content">
                <h3>操作詳細資訊</h3>
                <div class="modal-body">
                  <p><strong>操作時間：</strong>{{ formatDateTime(selectedLog?.created_at) }}</p>
                  <p><strong>表名：</strong>{{ getTableDisplayName(selectedLog?.table_name) }}</p>
                  <p><strong>操作類型：</strong>{{ selectedLog?.operation_type }}</p>
                  <p><strong>操作者：</strong>{{ selectedLog?.performer_name }}</p>
                  <p><strong>用戶類型：</strong>{{ selectedLog?.user_type }}</p>
                  <p><strong>操作對象：</strong>{{ selectedLog?.record_detail || selectedLog?.record_id }}</p>
                  <div class="changes-container">
                    <strong>變更內容：</strong>
                    <div v-html="formatChanges(selectedLog?.operation_detail)"></div>
                  </div>
                </div>
                <div class="modal-footer">
                  <button @click="showModal = false">關閉</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</template>

<script>
import axios from 'axios';
import SideBar from '../components/SideBar.vue';
import { adminMixin } from '../mixins/adminMixin';
import { timeMixin } from '../mixins/timeMixin';
import { API_PATHS, getApiUrl } from '../config/api';
import axiosInstance from '../config/axios';

export default {
  name: 'LogRecords',
  mixins: [adminMixin, timeMixin],
  components: {
    SideBar
  },
  data() {
    return {
      isSidebarActive: false,
      searchParams: {
        table_name: '',
        operation_type: '',
        start_date: '',
        end_date: '',
        user_type: '',
        page: 1
      },
      logs: [],
      totalPages: 0,
      currentPage: 1,
      showModal: false,
      selectedLog: null
    };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    },
    closeSidebar() {
      this.isSidebarActive = false;
    },
    async searchLogs() {
      try {
        const adminId = localStorage.getItem('admin_id');
        if (!adminId) {
          this.$router.push('/admin-login');
          return;
        }

        const response = await axiosInstance.post('/api/log/logs', {
          ...this.searchParams,
          page: this.currentPage,
          per_page: 50
        });

        if (response.data.status === 'success') {
          this.logs = response.data.data.logs;
          this.totalPages = response.data.data.total_pages;
        } else {
          throw new Error(response.data.message || '获取日志失败');
        }
      } catch (error) {
        console.error('Error fetching logs:', error);
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_id');
          this.$router.push('/admin-login');
        } else {
          alert('获取日志失败：' + (error.response?.data?.message || error.message));
        }
      }
    },
    changePage(page) {
      this.currentPage = page;
      this.searchLogs();
    },
    showLogDetail(log) {
      this.selectedLog = log;
      this.showModal = true;
    },
    formatDateTime(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleString('zh-TW');
    },
    getTableDisplayName(tableName) {
      const tableNames = {
        'orders': '訂單',
        'customers': '客戶',
        'products': '產品',
        'administrators': '管理員'
      };
      return tableNames[tableName] || tableName;
    },
    formatChanges(detail) {
      if (!detail) return '無變更內容';
      
      try {
        let detailObj = typeof detail === 'string' ? JSON.parse(detail) : detail;
        
        // 處理所有操作類型（新增、刪除、修改、審核）
        if (detailObj.message) {
          let html = `<div class="change-list">`;
          
          // 顯示訂單基本信息
          html += `
            <div class="change-item">
              <div class="field-name">訂單號：</div>
              <div class="new-value">${detailObj.message.order_number}</div>
            </div>`;

          // 顯示狀態信息
          if (detailObj.message.status) {
            if (typeof detailObj.message.status === 'string') {
              html += `
                <div class="change-item">
                  <div class="field-name">狀態：</div>
                  <div class="new-value">${detailObj.message.status}</div>
                </div>`;
            } else {
              html += `
                <div class="change-item">
                  <div class="field-name">狀態：</div>
                  <div class="change-content">
                    <span class="old-value">${detailObj.message.status.before}</span>
                    <span class="arrow">→</span>
                    <span class="new-value">${detailObj.message.status.after}</span>
                  </div>
                </div>`;
            }
          }

          // 顯示產品信息
          if (Array.isArray(detailObj.message.products)) {
            detailObj.message.products.forEach((product, index) => {
              html += `
                <div class="change-item">
                  <div class="field-name">產品 ${index + 1}：</div>
                  <div class="product-details">
                    <div>名稱：${product.name || ''}</div>`;

              // 如果是修改或審核操作，顯示變更內容
              if (product.changes) {
                if (product.changes.quantity) {
                  html += `
                    <div class="change-content">
                      <div class="field-name">數量：</div>
                      <span class="old-value">${product.changes.quantity.before}</span>
                      <span class="arrow">→</span>
                      <span class="new-value">${product.changes.quantity.after}</span>
                    </div>`;
                } else {
                  html += `<div>數量：${product.quantity || ''}</div>`;
                }

                if (product.changes.shipping_date) {
                  html += `
                    <div class="change-content">
                      <div class="field-name">出貨日期：</div>
                      <span class="old-value">${product.changes.shipping_date.before}</span>
                      <span class="arrow">→</span>
                      <span class="new-value">${product.changes.shipping_date.after}</span>
                    </div>`;
                } else {
                  html += `<div>出貨日期：${product.shipping_date || '待確認'}</div>`;
                }

                if (product.changes.note) {
                  html += `
                    <div class="change-content">
                      <div class="field-name">備註：</div>
                      <span class="old-value">${product.changes.note.before}</span>
                      <span class="arrow">→</span>
                      <span class="new-value">${product.changes.note.after}</span>
                    </div>`;
                } else if (product.changes.remark) {
                  html += `
                    <div class="change-content">
                      <div class="field-name">客戶備註：</div>
                      <span class="old-value">${product.changes.remark.before}</span>
                      <span class="arrow">→</span>
                      <span class="new-value">${product.changes.remark.after}</span>
                    </div>`;
                } else {
                  html += `<div>客戶備註：${product.remark || '-'}</div>`;
                }

                if (product.changes.supplier_note) {
                  html += `
                    <div class="change-content">
                      <div class="field-name">供應商備註：</div>
                      <span class="old-value">${product.changes.supplier_note.before}</span>
                      <span class="arrow">→</span>
                      <span class="new-value">${product.changes.supplier_note.after}</span>
                    </div>`;
                } else {
                  html += `<div>供應商備註：${product.supplier_note || '-'}</div>`;
                }
              } else {
                // 如果是新增或刪除操作，直接顯示值
                html += `
                  <div>數量：${product.quantity || ''}</div>
                  <div>出貨日期：${product.shipping_date || '待確認'}</div>
                  <div>客戶備註：${product.remark || '-'}</div>
                  <div>供應商備註：${product.supplier_note || '-'}</div>`;
              }

              html += `</div></div>`;
            });
          }

          html += `</div>`;
          return html;
        }
        
        return `<div class="simple-message">${JSON.stringify(detailObj, null, 2)}</div>`;
        
      } catch (e) {
        console.error('Error formatting changes:', e);
        return String(detail);
      }
    },
    
    getFieldDisplayName(field) {
      const fieldMap = {
        'order_confirmed': '訂單確認狀態',
        'status': '狀態',
        'shipping_date': '出貨日期',
        'quantity': '數量',
        'supplier_note': '供應商備註',
        'remark': '客戶備註',
        'note': '備註',
        'before': '原始值',
        'after': '變更後',
        'product': '產品',
        'customer': '客戶'
      };
      return fieldMap[field] || field;
    },
    getRecordDetail(log) {
      // 對於所有訂單操作（包括新增、修改、刪除、審核）
      if (log.table_name === 'orders') {
        try {
          // 嘗試解析 operation_detail
          const detail = typeof log.operation_detail === 'string' ? 
            JSON.parse(log.operation_detail) : log.operation_detail;
          
          // 如果有 message 且包含 order_number，直接返回 order_number
          if (detail?.message?.order_number) {
            return detail.message.order_number;  // 直接返回訂單號，不加前綴
          }
        } catch (e) {
          console.error('Error parsing operation detail:', e);
        }
      }
      
      // 如果不是訂單操作或解析失敗，返回原始的 record_detail 或 record_id
      return log.record_detail || log.record_id;
    }
  },
  mounted() {
    document.title = '操作紀錄查詢';
    this.searchLogs();
  }
};
</script>

<style>
/* 变更内容样式 - 全局作用域 */
.change-list {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
  text-align: center;
}

.change-item {
  margin: 8px 0;
  padding: 8px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  justify-content: center;
  align-items: center;
}

.change-header {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.1em;
}

.field-name {
  color: #666;
  font-weight: 500;
  margin-right: 8px;
}

.change-content {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  justify-content: center;
}

.old-value {
  color: #e74c3c;
  text-decoration: none;
  background-color: #ffebee;
  padding: 2px 6px;
  border-radius: 3px;
  position: relative;
}

.old-value::after {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 100%;
  height: 1px;
  background-color: #e74c3c;
  transform: rotate(-10deg);
}

.new-value {
  color: #27ae60;
  background-color: #e8f5e9;
  padding: 2px 6px;
  border-radius: 3px;
}

.arrow {
  color: #95a5a6;
  font-weight: bold;
  margin: 0 4px;
}

.change-detail {
  margin: 8px 0;
  padding: 8px;
  background-color: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-name {
  font-weight: 500;
  color: #2c3e50;
}

.new-status {
  color: #27ae60;
  font-weight: 500;
}

.shipping-date {
  color: #666;
  font-size: 0.9em;
  margin-left: auto;
}

.simple-message {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  color: #2c3e50;
}

.field-value {
  color: #2c3e50;
}

.product-details {
  margin-left: 20px;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.product-details > div {
  margin: 4px 0;
}

.new-value {
  color: #27ae60;
  font-weight: 500;
}
</style>

<style scoped>
.search-container {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.search-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-item select,
.search-item input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

.search-button {
  background-color: #4CAF50;
  color: white;
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-button:hover {
  background-color: #45a049;
}

.log-list {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.log-list th,
.log-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.log-list th {
  background-color: #f5f5f5;
}

.detail-button {
  background-color: #2196F3;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.detail-button:hover {
  background-color: #1976D2;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background-color: white;
  cursor: pointer;
}

.pagination button:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-body {
  margin: 20px 0;
}

.changes-container {
  margin-top: 10px;
}

.changes-container pre {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  white-space: pre-wrap;
  font-family: monospace;
  margin: 0;
  line-height: 1.5;
}

.table-border {
  margin: 0;
  padding: 0;
  color: #666;
  line-height: 1;
}

.table-row {
  font-family: monospace;
  white-space: pre;
  padding: 8px 0;
  color: #333;
}

.log-detail-line {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  font-family: inherit;
}

.log-detail-line:last-child {
  border-bottom: none;
}

.modal-footer {
  text-align: right;
}

.modal-footer button {
  background-color: #4CAF50;
  color: white;
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-footer button:hover {
  background-color: #45a049;
}
</style> 