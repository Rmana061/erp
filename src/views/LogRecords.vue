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
          console.log('後端返回的日誌數據:', response.data);
          this.logs = response.data.data;
          this.totalPages = Math.ceil(response.data.total_count / 50);
          this.currentPage = this.searchParams.page;
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
        console.log('原始detail:', detail);
        let detailObj = typeof detail === 'string' ? JSON.parse(detail) : detail;
        console.log('解析后的detailObj:', detailObj);
        
        // 處理所有操作類型（新增、刪除、修改、審核）
        if (detailObj.message) {
          let html = `<div class="change-list">`;
          
          // 處理管理員相關日誌
          if (detailObj.message.admin) {
            const adminInfo = detailObj.message.admin;
            
            // 判斷操作類型，修改操作只顯示變更詳情
            if (detailObj.operation_type !== '修改') {
              // 新增和刪除操作顯示管理員信息
              html += `
                <div class="change-item admin-info">
                  <div class="admin-header">管理員資訊</div>
                  <div class="admin-details">
                    <div class="change-row">
                      <div class="field-name">人員帳號</div>
                      <div class="field-value">${adminInfo.admin_account || '-'}</div>
                    </div>
                    <div class="change-row">
                      <div class="field-name">人員姓名</div>
                      <div class="field-value">${adminInfo.admin_name || '-'}</div>
                    </div>
                    <div class="change-row">
                      <div class="field-name">人員工號</div>
                      <div class="field-value">${adminInfo.staff_no || '-'}</div>
                    </div>
                    <div class="change-row">
                      <div class="field-name">人員權限</div>
                      <div class="field-value">${this.convertPermissionToText(adminInfo.permission_level) || '-'}</div>
                    </div>
                  </div>
                </div>`;
            }
            
            // 如果有變更信息，顯示變更部分（修改操作）
            if (detailObj.message.changes) {
              html += `
                <div class="change-item">
                  <div class="change-header">變更詳情</div>
                  <div class="change-details">`;
              
              for (const [field, change] of Object.entries(detailObj.message.changes)) {
                let beforeValue = change.before;
                let afterValue = change.after;
                
                // 對人員權限進行特殊處理，轉換為中文
                if (field === '人員權限') {
                  beforeValue = this.convertPermissionToText(beforeValue);
                  afterValue = this.convertPermissionToText(afterValue);
                }
                
                html += `
                  <div class="change-row">
                    <div class="field-name">${field}</div>
                    <div class="change-values">
                      <span class="old-value">${beforeValue}</span>
                      <span class="arrow">→</span>
                      <span class="new-value">${afterValue}</span>
                    </div>
                  </div>`;
              }
              
              html += `</div></div>`;
            }
            
            html += `</div>`;
            return html;
          } 
          // 處理訂單相關日誌
          else if (detailObj.message.order_number) {
            // 顯示訂單基本信息
            html += `
              <div class="change-item order-info">
                <div class="field-name">訂單號：</div>
                <div class="new-value">${detailObj.message.order_number || ''}</div>
              </div>`;

            // 顯示狀態信息
            if (detailObj.message.status) {
              if (typeof detailObj.message.status === 'string') {
                html += `
                  <div class="change-item order-info">
                    <div class="field-name">狀態：</div>
                    <div class="new-value">${detailObj.message.status}</div>
                  </div>`;
              } else {
                html += `
                  <div class="change-item order-info">
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
              console.log(`處理${detailObj.message.products.length}個產品的變更記錄`);
              detailObj.message.products.forEach((product, index) => {
                html += `
                  <div class="change-item">
                    <div class="product-header">產品 ${index + 1}：${product.name || ''}</div>
                    <div class="product-details">`;

                // 如果是修改或審核操作，顯示變更內容
                if (product.changes) {
                  html += `<div class="product-changes">`;
                  
                  // 檢查並顯示數量變更
                  if (product.changes.quantity) {
                    html += `
                      <div class="change-row">
                        <div class="field-name">數量</div>
                        <div class="change-values">
                          <span class="old-value">${product.changes.quantity.before}</span>
                          <span class="arrow">→</span>
                          <span class="new-value">${product.changes.quantity.after}</span>
                        </div>
                      </div>`;
                  } else {
                    html += `
                      <div class="change-row">
                        <div class="field-name">數量</div>
                        <div class="field-value">${product.quantity || '-'}</div>
                      </div>`;
                  }

                  // 檢查並顯示出貨日期變更
                  if (product.changes.shipping_date) {
                    html += `
                      <div class="change-row">
                        <div class="field-name">出貨日期</div>
                        <div class="change-values">
                          <span class="old-value">${product.changes.shipping_date.before}</span>
                          <span class="arrow">→</span>
                          <span class="new-value">${product.changes.shipping_date.after}</span>
                        </div>
                      </div>`;
                  } else {
                    html += `
                      <div class="change-row">
                        <div class="field-name">出貨日期</div>
                        <div class="field-value">${product.shipping_date || '-'}</div>
                      </div>`;
                  }

                  // 檢查並顯示客戶備註變更
                  if (product.changes.remark) {
                    html += `
                      <div class="change-row">
                        <div class="field-name">客戶備註</div>
                        <div class="change-values">
                          <span class="old-value">${product.changes.remark.before}</span>
                          <span class="arrow">→</span>
                          <span class="new-value">${product.changes.remark.after}</span>
                        </div>
                      </div>`;
                  } else if (product.remark) {
                    html += `
                      <div class="change-row">
                        <div class="field-name">客戶備註</div>
                        <div class="field-value">${product.remark || '-'}</div>
                      </div>`;
                  }

                  // 檢查並顯示供應商備註變更
                  if (product.changes.supplier_note) {
                    html += `
                      <div class="change-row">
                        <div class="field-name">供應商備註</div>
                        <div class="change-values">
                          <span class="old-value">${product.changes.supplier_note.before}</span>
                          <span class="arrow">→</span>
                          <span class="new-value">${product.changes.supplier_note.after}</span>
                        </div>
                      </div>`;
                  } else {
                    html += `
                      <div class="change-row">
                        <div class="field-name">供應商備註</div>
                        <div class="field-value">${product.supplier_note || '-'}</div>
                      </div>`;
                  }
                  
                  // 檢查並顯示狀態變更
                  if (product.changes.status) {
                    html += `
                      <div class="change-row">
                        <div class="field-name">狀態</div>
                        <div class="change-values">
                          <span class="old-value">${product.changes.status.before}</span>
                          <span class="arrow">→</span>
                          <span class="new-value">${product.changes.status.after}</span>
                        </div>
                      </div>`;
                  }
                  
                  html += `</div>`;
                } else {
                  // 如果是新增或刪除操作，直接顯示值
                  html += `
                    <div class="product-changes">
                      <div class="change-row">
                        <div class="field-name">數量</div>
                        <div class="field-value">${product.quantity || ''}</div>
                      </div>
                      <div class="change-row">
                        <div class="field-name">出貨日期</div>
                        <div class="field-value">${product.shipping_date || '待確認'}</div>
                      </div>
                      <div class="change-row">
                        <div class="field-name">客戶備註</div>
                        <div class="field-value">${product.remark || '-'}</div>
                      </div>
                      <div class="change-row">
                        <div class="field-name">供應商備註</div>
                        <div class="field-value">${product.supplier_note || '-'}</div>
                      </div>
                    </div>`;
                }

                html += `</div></div>`;
              });
            } else if (typeof detailObj.message === 'string') {
              // 嘗試解析字符串格式的消息
              try {
                const messageParts = detailObj.message.split('、');
                const parsedMessage = {};
                
                for (const part of messageParts) {
                  if (part.includes(':')) {
                    const [key, value] = part.split(':');
                    parsedMessage[key.trim()] = value.trim();
                  }
                }
                
                // 如果解析成功，顯示產品信息
                if (parsedMessage['產品']) {
                  html += `
                    <div class="change-item">
                      <div class="product-header">產品：${parsedMessage['產品'] || ''}</div>
                      <div class="product-details">
                        <div class="product-changes">
                          <div class="change-row">
                            <div class="field-name">數量</div>
                            <div class="field-value">${parsedMessage['數量'] || ''}</div>
                          </div>
                          <div class="change-row">
                            <div class="field-name">出貨日期</div>
                            <div class="field-value">${parsedMessage['出貨日期'] || '待確認'}</div>
                          </div>
                          <div class="change-row">
                            <div class="field-name">客戶備註</div>
                            <div class="field-value">${parsedMessage['備註'] || '-'}</div>
                          </div>
                          <div class="change-row">
                            <div class="field-name">供應商備註</div>
                            <div class="field-value">${parsedMessage['供應商備註'] || '-'}</div>
                          </div>
                        </div>
                      </div>
                    </div>`;
                } else {
                  // 如果無法解析為產品信息，直接顯示原始消息
                  html += `
                    <div class="change-item order-info">
                      <div class="field-name">詳細信息：</div>
                      <div class="simple-message">${detailObj.message}</div>
                    </div>`;
                }
              } catch (e) {
                console.error('解析消息字符串失敗:', e);
                html += `
                  <div class="change-item order-info">
                    <div class="field-name">詳細信息：</div>
                    <div class="simple-message">${detailObj.message}</div>
                  </div>`;
              }
            }
            
            html += `</div>`;
            return html;
          } else {
            // 處理其他類型的消息
            html += `
              <div class="change-item order-info">
                <div class="field-name">詳細信息：</div>
                <div class="simple-message">${JSON.stringify(detailObj.message, null, 2)}</div>
              </div>`;
            html += `</div>`;
            return html;
          }
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
    convertPermissionToText(permissionId) {
      // 将权限ID转换为对应的中文描述
      const permissionMap = {
        '1': '最高權限',
        '2': '審核權限',
        '3': '普通權限',
        '4': '檢視權限'
      };
      return permissionMap[permissionId] || `${permissionId}`;
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
      
      // 對於管理員操作（包括新增、修改、刪除）
      if (log.table_name === 'administrators') {
        try {
          // 嘗試解析 operation_detail
          const detail = typeof log.operation_detail === 'string' ? 
            JSON.parse(log.operation_detail) : log.operation_detail;
          
          // 如果有 message 且包含 admin，返回管理員姓名
          if (detail?.message?.admin?.admin_name) {
            return detail.message.admin.admin_name;  // 返回管理員姓名
          }
        } catch (e) {
          console.error('Error parsing admin operation detail:', e);
        }
      }
      
      // 如果不是訂單或管理員操作或解析失敗，返回原始的 record_detail 或 record_id
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
  text-align: left;
}

.change-item {
  margin: 12px 0;
  padding: 12px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

/* 訂單號和狀態項目特殊樣式 */
.change-item.order-info {
  flex-direction: row;
  justify-content: center;
  align-items: center;
  text-align: center;
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
  min-width: 100px;
  text-align: right;
}

.change-content {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  justify-content: center;
}

/* 新增表格式布局 */
.product-details {
  width: 100%;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.product-details > div:first-child {
  font-weight: 500;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.product-changes {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 8px;
  margin-top: 8px;
}

.change-row {
  display: flex;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px dashed #eee;
}

.change-row:last-child {
  border-bottom: none;
}

.change-values {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
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
  flex: 1;
}

.product-header {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1.05em;
  background-color: #e8f4f8;
  padding: 8px 12px;
  border-radius: 4px;
  width: 100%;
  border-left: 3px solid #2196F3;
}

.product-details {
  width: 100%;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.product-details > div:first-child {
  font-weight: 500;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

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