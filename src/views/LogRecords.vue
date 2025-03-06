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
      selectedLog: null,
      // 定義需要顯示的客戶欄位及其顯示名稱
      customerFields: {
        'company_name': '公司名稱',
        'username': '帳號',
        'password': '密碼',
        'viewable_products': '可購產品',
        'line_account': 'LINE帳號',
        'contact_person': '聯絡人',
        'phone': '電話',
        'email': 'Email',
        'address': '地址',
        'remark': '備註'
      },
      // 表名顯示映射
      tableNames: {
        'orders': '訂單',
        'customers': '客戶',
        'products': '產品',
        'administrators': '管理員'
      },
      // 字段顯示名稱映射
      fieldDisplayMap: {
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
      },
      // 權限ID映射
      permissionMap: {
        '1': '最高權限',
        '2': '審核權限',
        '3': '普通權限',
        '4': '檢視權限'
      }
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
      return this.tableNames[tableName] || tableName;
    },
    formatChanges(detail) {
      if (!detail) return '無變更內容';
      
      try {
        console.log('原始detail:', detail);
        let detailObj = typeof detail === 'string' ? JSON.parse(detail) : detail;
        console.log('解析后的detailObj:', detailObj);
        
        // 處理所有操作類型（新增、刪除、修改、審核）
        if (detailObj.message) {
          let html = this.startChangeList();
          
          // 處理客戶相關日誌
          if (detailObj.message.customer || 
              (detailObj.message.new_data && (detailObj.message.new_data.company_name || detailObj.message.new_data.username))) {
            html += this.formatCustomerChanges(detailObj);
          }
          // 處理管理員相關日誌
          else if (detailObj.message.admin) {
            html += this.formatAdminChanges(detailObj);
          } 
          // 處理訂單相關日誌
          else if (detailObj.message.order_number) {
            html += this.formatOrderChanges(detailObj);
          } else {
            // 處理其他類型的消息
            html += this.generateSimpleMessage('詳細信息', JSON.stringify(detailObj.message, null, 2));
          }
          
          html += this.endChangeList();
          return html;
        }
        
        return this.wrapInSimpleMessage(JSON.stringify(detailObj, null, 2));
        
      } catch (e) {
        console.error('Error formatting changes:', e);
        return String(detail);
      }
    },

    // 處理客戶相關日誌的輔助方法
    formatCustomerChanges(detailObj) {
      // 處理客戶數據的顯示
      const customerData = detailObj.operation_type === '修改' ? 
        { old: detailObj.message.old_data, new: detailObj.message.new_data } : 
        (detailObj.operation_type === '新增' ? { new: detailObj.message.customer || detailObj.message.new_data } : 
        { old: detailObj.message.customer || detailObj.message.old_data });
      
      let html = this.startChangeItem('customer-info');
      html += this.generateSectionHeader('客戶資訊', 'customer-header');
      html += this.startChangeDetails('customer-details');
      
      // 對於新增和刪除操作，顯示完整資訊
      if (detailObj.operation_type === '新增' || detailObj.operation_type === '刪除') {
        const data = detailObj.operation_type === '新增' ? customerData.new : customerData.old;
        
        // 按照定義的顺序显示字段，而不是直接遍历原始数据
        Object.keys(this.customerFields).forEach(field => {
          if (data && (data[field] !== undefined || (field === 'password' && data.password_changed))) {
            if (field === 'password' && data.password_changed) {
              html += this.generatePasswordChangeRow(this.customerFields[field]);
            } else if (field !== 'password') {
              html += this.generateFieldRow(this.customerFields[field], data[field] || '-');
            }
          }
        });
      } 
      // 對於修改操作，優先使用changes字段顯示變更詳情
      else if (detailObj.operation_type === '修改' || detailObj.operation_type.includes('修改')) {
        // 如果有changes字段，優先使用它
        if (detailObj.message.changes) {
          // 按照定義的顺序检查并显示变更字段
          Object.keys(this.customerFields).forEach(field => {
            // 特殊處理密碼欄位
            if (field === 'password' && (detailObj.message.changes.__password_changed__ || detailObj.message.password_changed)) {
              html += this.generatePasswordChangeRow(this.customerFields[field]);
              return; // 繼續下一個字段
            }
            
            // 跳過特殊標記字段
            if (field === '__password_changed__') return;
            
            const change = detailObj.message.changes[field];
            const label = this.customerFields[field];
            
            // 只处理在changes中存在且有before和after的字段
            if (change && typeof change === 'object' && 'before' in change && 'after' in change) {
              html += this.generateChangeRow(label, change.before || '-', change.after || '-');
            }
          });
        }
        // 如果没有changes字段，则使用old_data和new_data进行比较
        else if (customerData.old && customerData.new) {
          // 按照定義的顺序比较并显示变更字段
          Object.keys(this.customerFields).forEach(field => {
            // 特殊處理密碼欄位
            if (field === 'password' && customerData.new.password_changed) {
              html += this.generatePasswordChangeRow(this.customerFields[field]);
              return; // 繼續下一個字段
            }
            
            const oldValue = customerData.old[field];
            const newValue = customerData.new[field];
            const label = this.customerFields[field];
            
            // 只顯示有變更的欄位
            if (oldValue !== newValue && field !== 'password') {
              html += this.generateChangeRow(label, oldValue || '-', newValue || '-');
            }
          });
        }
      }
      
      html += this.endChangeDetails();
      html += this.endChangeItem();
      return html;
    },

    // 處理管理員相關日誌的輔助方法
    formatAdminChanges(detailObj) {
      const adminInfo = detailObj.message.admin;
      let html = '';
      
      // 判斷操作類型，修改操作只顯示變更詳情
      if (detailObj.operation_type !== '修改') {
        // 新增和刪除操作顯示管理員信息
        html += this.startChangeItem('admin-info');
        html += this.generateSectionHeader('管理員資訊', 'admin-header');
        html += this.startChangeDetails('admin-details');
        
        html += this.generateFieldRow('人員帳號', adminInfo.admin_account || '-');
        html += this.generateFieldRow('人員姓名', adminInfo.admin_name || '-');
        html += this.generateFieldRow('人員工號', adminInfo.staff_no || '-');
        html += this.generateFieldRow('人員權限', this.convertPermissionToText(adminInfo.permission_level) || '-');
        
        html += this.endChangeDetails();
        html += this.endChangeItem();
      }
      
      // 如果有變更信息，顯示變更部分（修改操作）
      if (detailObj.message.changes) {
        html += this.startChangeItem();
        html += this.generateSectionHeader('變更詳情', 'change-header');
        html += this.startChangeDetails('change-details');
        
        for (const [field, change] of Object.entries(detailObj.message.changes)) {
          let beforeValue = change.before;
          let afterValue = change.after;
          
          // 對人員權限進行特殊處理，轉換為中文
          if (field === '人員權限') {
            beforeValue = this.convertPermissionToText(beforeValue);
            afterValue = this.convertPermissionToText(afterValue);
          }
          
          html += this.generateChangeRow(field, beforeValue, afterValue);
        }
        
        html += this.endChangeDetails();
        html += this.endChangeItem();
      }
      
      return html;
    },

    // 處理訂單相關日誌的輔助方法
    formatOrderChanges(detailObj) {
      let html = '';
      
      // 顯示訂單基本信息
      html += this.generateOrderInfoRow('訂單號', detailObj.message.order_number || '');

      // 顯示狀態信息
      if (detailObj.message.status) {
        if (typeof detailObj.message.status === 'string') {
          html += this.generateOrderInfoRow('狀態', detailObj.message.status);
        } else {
          html += this.generateOrderStatusChangeRow(detailObj.message.status.before, detailObj.message.status.after);
        }
      }

      // 顯示產品信息
      if (Array.isArray(detailObj.message.products)) {
        console.log(`處理${detailObj.message.products.length}個產品的變更記錄`);
        detailObj.message.products.forEach((product, index) => {
          html += this.formatProductChange(product, index);
        });
      } else if (typeof detailObj.message === 'string') {
        html += this.formatMessageString(detailObj.message);
      }
      
      return html;
    },

    // 處理產品變更的輔助方法
    formatProductChange(product, index) {
      let html = this.startChangeItem();
      html += this.generateSectionHeader(`產品 ${index + 1}：${product.name || ''}`, 'product-header');
      html += this.startChangeDetails('product-details');

      // 如果是修改或審核操作，顯示變更內容
      if (product.changes) {
        html += this.startProductChanges();
        
        // 檢查並顯示數量變更
        if (product.changes.quantity) {
          html += this.generateChangeRow('數量', product.changes.quantity.before, product.changes.quantity.after);
        } else {
          html += this.generateFieldRow('數量', product.quantity || '-');
        }

        // 檢查並顯示出貨日期變更
        if (product.changes.shipping_date) {
          html += this.generateChangeRow('出貨日期', product.changes.shipping_date.before, product.changes.shipping_date.after);
        } else {
          html += this.generateFieldRow('出貨日期', product.shipping_date || '-');
        }

        // 檢查並顯示客戶備註變更
        if (product.changes.remark) {
          html += this.generateChangeRow('客戶備註', product.changes.remark.before, product.changes.remark.after);
        } else if (product.remark) {
          html += this.generateFieldRow('客戶備註', product.remark || '-');
        }

        // 檢查並顯示供應商備註變更
        if (product.changes.supplier_note) {
          html += this.generateChangeRow('供應商備註', product.changes.supplier_note.before, product.changes.supplier_note.after);
        } else {
          html += this.generateFieldRow('供應商備註', product.supplier_note || '-');
        }
        
        // 檢查並顯示狀態變更
        if (product.changes.status) {
          html += this.generateChangeRow('狀態', product.changes.status.before, product.changes.status.after);
        }
        
        html += this.endProductChanges();
      } else {
        // 如果是新增或刪除操作，直接顯示值
        html += this.startProductChanges();
        html += this.generateFieldRow('數量', product.quantity || '');
        html += this.generateFieldRow('出貨日期', product.shipping_date || '待確認');
        html += this.generateFieldRow('客戶備註', product.remark || '-');
        html += this.generateFieldRow('供應商備註', product.supplier_note || '-');
        html += this.endProductChanges();
      }

      html += this.endChangeDetails();
      html += this.endChangeItem();
      return html;
    },

    // 處理字符串消息的輔助方法
    formatMessageString(message) {
      let html = '';
      // 嘗試解析字符串格式的消息
      try {
        const messageParts = message.split('、');
        const parsedMessage = {};
        
        for (const part of messageParts) {
          if (part.includes(':')) {
            const [key, value] = part.split(':');
            parsedMessage[key.trim()] = value.trim();
          }
        }
        
        // 如果解析成功，顯示產品信息
        if (parsedMessage['產品']) {
          html += this.startChangeItem();
          html += this.generateSectionHeader(`產品：${parsedMessage['產品'] || ''}`, 'product-header');
          html += this.startChangeDetails('product-details');
          html += this.startProductChanges();
          
          html += this.generateFieldRow('數量', parsedMessage['數量'] || '');
          html += this.generateFieldRow('出貨日期', parsedMessage['出貨日期'] || '待確認');
          html += this.generateFieldRow('客戶備註', parsedMessage['備註'] || '-');
          html += this.generateFieldRow('供應商備註', parsedMessage['供應商備註'] || '-');
          
          html += this.endProductChanges();
          html += this.endChangeDetails();
          html += this.endChangeItem();
        } else {
          // 如果無法解析為產品信息，直接顯示原始消息
          html += this.generateSimpleMessage('詳細信息', message);
        }
      } catch (e) {
        console.error('解析消息字符串失敗:', e);
        html += this.generateSimpleMessage('詳細信息', message);
      }
      return html;
    },

    // HTML模板輔助方法
    startChangeList() {
      return `<div class="change-list">`;
    },
    
    endChangeList() {
      return `</div>`;
    },
    
    startChangeItem(className = '') {
      return `<div class="change-item ${className}">`;
    },
    
    endChangeItem() {
      return `</div>`;
    },
    
    startChangeDetails(className = '') {
      return `<div class="${className}">`;
    },
    
    endChangeDetails() {
      return `</div>`;
    },
    
    startProductChanges() {
      return `<div class="product-changes">`;
    },
    
    endProductChanges() {
      return `</div>`;
    },
    
    generateSectionHeader(text, className = '') {
      return `<div class="${className}">${text}</div>`;
    },
    
    generateSimpleMessage(label, message) {
      return `
        <div class="change-item order-info">
          <div class="field-name">${label}：</div>
          <div class="simple-message">${message}</div>
        </div>`;
    },
    
    wrapInSimpleMessage(message) {
      return `<div class="simple-message">${message}</div>`;
    },
    
    generateOrderInfoRow(label, value) {
      return `
        <div class="change-item order-info">
          <div class="field-name">${label}：</div>
          <div class="new-value">${value}</div>
        </div>`;
    },
    
    generateOrderStatusChangeRow(beforeStatus, afterStatus) {
      return `
        <div class="change-item order-info">
          <div class="field-name">狀態：</div>
          <div class="change-content">
            <span class="old-value">${beforeStatus}</span>
            <span class="arrow">→</span>
            <span class="new-value">${afterStatus}</span>
          </div>
        </div>`;
    },

    // 生成標準字段行的輔助方法
    generateFieldRow(label, value) {
      return `
        <div class="change-row">
          <div class="field-name">${label}</div>
          <div class="field-value">${value}</div>
        </div>`;
    },

    // 生成標準變更行的輔助方法
    generateChangeRow(label, oldValue, newValue) {
      return `
        <div class="change-row">
          <div class="field-name">${label}</div>
          <div class="change-values">
            <span class="old-value">${oldValue}</span>
            <span class="arrow">→</span>
            <span class="new-value">${newValue}</span>
          </div>
        </div>`;
    },

    // 生成密碼變更行的輔助方法
    generatePasswordChangeRow(label) {
      return `
        <div class="change-row">
          <div class="field-name">${label}</div>
          <div class="change-values">
            <span class="old-value">*****</span>
            <span class="arrow">→</span>
            <span class="new-value">已更新密碼</span>
          </div>
        </div>`;
    },

    getFieldDisplayName(field) {
      return this.fieldDisplayMap[field] || field;
    },
    
    convertPermissionToText(permissionId) {
      // 将权限ID转换为对应的中文描述
      return this.permissionMap[permissionId] || `${permissionId}`;
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
      
      // 對於客戶操作（包括新增、修改、刪除）
      if (log.table_name === 'customers') {
        try {
          // 嘗試解析 operation_detail
          const detail = typeof log.operation_detail === 'string' ? 
            JSON.parse(log.operation_detail) : log.operation_detail;
          
          // 優先顯示客戶名稱，不管是否有密碼變更
          // 新增和修改操作優先從new_data中獲取
          if (detail?.message?.new_data?.username) {
            return detail.message.new_data.username;  // 返回客戶名稱
          } 
          // 刪除操作或備用情況從old_data中獲取
          else if (detail?.message?.old_data?.username) {
            return detail.message.old_data.username;  // 返回客戶名稱
          } 
          // 備用：從customer直接獲取
          else if (detail?.message?.customer?.username) {
            return detail.message.customer.username;  // 返回客戶名稱
          }
          // 如果沒有username，才嘗試獲取company_name
          else if (detail?.message?.new_data?.company_name) {
            return detail.message.new_data.company_name;  // 返回公司名稱
          }
          else if (detail?.message?.old_data?.company_name) {
            return detail.message.old_data.company_name;  // 返回公司名稱
          }
          else if (detail?.message?.customer?.company_name) {
            return detail.message.customer.company_name;  // 返回公司名稱
          }
          // 最後才考慮使用ID
          else if (detail?.message?.new_data?.id) {
            return `客戶ID: ${detail.message.new_data.id}`;  // 返回客戶ID
          } 
          else if (detail?.message?.old_data?.id) {
            return `客戶ID: ${detail.message.old_data.id}`;  // 返回客戶ID
          } 
          else if (detail?.message?.customer?.id) {
            return `客戶ID: ${detail.message.customer.id}`;  // 返回客戶ID
          }
        } catch (e) {
          console.error('Error parsing customer operation detail:', e);
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