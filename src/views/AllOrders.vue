<!-- 所有訂單 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,</span>
        <span>{{ currentTime }}</span>
      </div>
      
      <div class="content-wrapper">
        <h2>所有訂單</h2>
        <div class="action-buttons">
          <button 
            class="action-button" 
            @click="exportReport"
            v-permission="'can_approve_orders'">
            ↓ 訂單匯出
          </button>
        </div>

        <!-- 搜索欄位 -->
        <div class="search-panel compact">
          <div class="search-panel-body">
            <div class="search-form">
              <div class="search-form-row">
                <div class="search-form-item">
                  <input 
                    type="date" 
                    v-model="searchFilters.startDate"
                    :max="searchFilters.endDate || maxShippingDate"
                    class="search-field"
                    placeholder="開始日期">
                  <span class="date-separator">~</span>
                  <input 
                    type="date" 
                    v-model="searchFilters.endDate"
                    :min="searchFilters.startDate || minShippingDate"
                    :max="maxShippingDate"
                    class="search-field"
                    placeholder="結束日期">
                </div>
                <div class="search-form-item">
                  <input 
                    type="text" 
                    v-model="searchFilters.company" 
                    placeholder="公司名稱"
                    class="search-field">
                </div>
                <div class="search-form-item">
                  <input 
                    type="text" 
                    v-model="searchFilters.product" 
                    placeholder="產品名稱"
                    class="search-field">
                </div>
                <div class="search-form-item">
                  <input 
                    type="text" 
                    v-model="searchFilters.orderNumber" 
                    placeholder="訂單編號"
                    class="search-field">
                </div>
                <div class="search-actions">
                  <button class="reset-btn" @click="resetFilters">
                    <i class="fas fa-undo-alt"></i>重置
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>建立日期</th>
                <th>客戶</th>
                <th>訂單編號</th>
                <th>品項</th>
                <th>數量</th>
                <th>單位</th>
                <th>出貨日期</th>
                <th>備註</th>
                <th>供應商備註</th>
                <th>狀態</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="(order, orderIndex) in paginatedOrders" :key="order.orderNumber">
                <tr v-for="(item, itemIndex) in order.items" 
                    :key="order.orderNumber + '-' + itemIndex"
                    :class="{ 
                      'first-product': itemIndex === 0,
                      'approved': item.status === '已確認', 
                      'rejected': item.status === '已取消',
                      'shipped': item.status === '已出貨'
                    }">
                  <td>{{ itemIndex === 0 ? formatDateTime(order.date) : '' }}</td>
                  <td>{{ itemIndex === 0 ? order.customer : '' }}</td>
                  <td>{{ itemIndex === 0 ? order.orderNumber : '' }}</td>
                  <td>{{ item.item }}</td>
                  <td>
                    <template v-if="selectedOrder && selectedOrder.orderNumber === order.orderNumber">
                      <input 
                        type="number" 
                        v-model.number="item.tempQuantity"
                        :min="1"
                        class="quantity-input"
                        style="width: 80px;"
                      >
                    </template>
                    <template v-else>
                      {{ item.quantity }}
                    </template>
                  </td>
                  <td>{{ item.unit }}</td>
                  <td>{{ formatDate(item.shipping_date) }}</td>
                  <td>{{ item.remark || '-' }}</td>
                  <td>{{ item.supplier_note || '-' }}</td>
                  <td>
                    <span class="status-badge" :class="item.status">{{ item.status }}</span>
                  </td>
                  <td>
                    <div class="table-button-group" v-if="itemIndex === 0 && allItemsPending(order.items)">
                      <button 
                        class="table-button" 
                        @click="handleApprove(order)"
                        v-permission="'can_approve_orders'">
                        審核
                      </button>
                    </div>
                    <div class="table-button-group" v-else-if="itemIndex === 0 && hasConfirmedItems(order.items)">
                      <button 
                        class="table-button" 
                        @click="handleComplete(order)"
                        v-permission="'can_approve_orders'">
                        完成
                      </button>
                    </div>
                    <span v-else-if="itemIndex === 0" class="completed-text">已完成</span>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
        
        <!-- 分頁控制 -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1">
            上一頁
          </button>
          <span>{{ currentPage }} / {{ totalPages }}</span>
          <button 
            @click="currentPage++" 
            :disabled="currentPage === totalPages">
            下一頁
          </button>
        </div>
        
        <div class="notification">
          結果客戶可在LINE查詢
        </div>
      </div>
    </div>

    <!-- 審核確認對話框 -->
    <div class="modal" v-if="showConfirmModal">
      <div class="modal-content order-review">
        <h3>訂單審核 - {{ selectedOrder?.orderNumber }}</h3>
        
        <div class="order-items">
          <table class="review-table">
            <thead>
              <tr>
                <th>品項</th>
                <th>數量</th>
                <th>單位</th>
                <th>出貨日期</th>
                <th>備註</th>
                <th>供應商備註</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in selectedOrder?.items" :key="index">
                <td>{{ item.item }}</td>
                <td>
                  <input 
                    type="number"
                    v-model.number="item.tempQuantity"
                    :min="1"
                    class="quantity-input"
                  >
                </td>
                <td>{{ item.unit }}</td>
                <td>
                  <input 
                    type="date" 
                    v-model="item.tempShippingDate"
                    :min="minShippingDate"
                    :max="maxShippingDate"
                    :disabled="item.tempStatus === '已取消'"
                    @change="validateShippingDate(item)">
                </td>
                <td>{{ item.remark }}</td>
                <td>
                  <input 
                    type="text" 
                    v-model="item.tempSupplierNote"
                    placeholder="請輸入供應商備註">
                </td>
                <td>
                  <select v-model="item.tempStatus">
                    <option value="已確認">核准</option>
                    <option value="已取消">駁回</option>
                  </select>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="modal-buttons">
          <button 
            class="confirm-btn" 
            @click="confirmOrderUpdate()"
            :disabled="!isValidForConfirmation">
            確認
          </button>
          <button class="cancel-btn" @click="closeConfirmModal">返回</button>
        </div>
      </div>
    </div>

    <!-- 完成出貨確認對話框 -->
    <div class="modal" v-if="showCompleteModal">
      <div class="modal-content">
        <h3>確認出貨完成</h3>
        <p>確認將訂單 {{ selectedOrder?.orderNumber }} 標記為已出貨？</p>
        <div class="modal-buttons">
          <button class="confirm-btn" @click="confirmComplete">確認</button>
          <button class="cancel-btn" @click="closeCompleteModal">取消</button>
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import { timeMixin } from '../mixins/timeMixin';
import { adminMixin } from '../mixins/adminMixin';
import SideBar from '../components/SideBar.vue';
import axios from 'axios';
import { API_BASE_URL, API_PATHS, getApiUrl } from '../config/api';
import * as XLSX from 'xlsx';

export default {
  name: 'AllOrders',
  components: {
    SideBar
  },
  mixins: [timeMixin, adminMixin],
  data() {
    return {
      orders: [],
      showConfirmModal: false,
      showCompleteModal: false,
      selectedOrder: null,
      currentPage: 1,
      itemsPerPage: 10,
      searchFilters: {
        startDate: '',
        endDate: '',
        company: '',
        orderNumber: '',
        product: '',
        status: ''
      }
    };
  },
  computed: {
    minShippingDate() {
      const today = new Date();
      return today.toISOString().split('T')[0];
    },
    maxShippingDate() {
      const maxDate = new Date();
      maxDate.setMonth(maxDate.getMonth() + 3);
      return maxDate.toISOString().split('T')[0];
    },
    filteredOrders() {
      let filtered = [...this.orders];
      
      if (this.searchFilters.startDate) {
        const startDate = new Date(this.searchFilters.startDate);
        filtered = filtered.filter(order => new Date(order.date) >= startDate);
      }
      if (this.searchFilters.endDate) {
        const endDate = new Date(this.searchFilters.endDate);
        endDate.setHours(23, 59, 59);
        filtered = filtered.filter(order => new Date(order.date) <= endDate);
      }
      
      if (this.searchFilters.company) {
        filtered = filtered.filter(order => 
          order.customer.toLowerCase().includes(this.searchFilters.company.toLowerCase())
        );
      }
      
      if (this.searchFilters.orderNumber) {
        filtered = filtered.filter(order => 
          order.order_number.toLowerCase().includes(this.searchFilters.orderNumber.toLowerCase())
        );
      }
      
      if (this.searchFilters.product) {
        filtered = filtered.filter(order => 
          order.item.toLowerCase().includes(this.searchFilters.product.toLowerCase())
        );
      }
      
      return filtered;
    },
    groupedOrders() {
      const grouped = {};
      console.log('開始處理訂單分組，原始數據:', this.filteredOrders);
      
      this.filteredOrders.forEach(order => {
        if (!grouped[order.order_number]) {
          grouped[order.order_number] = {
            orderNumber: order.order_number,
            date: order.date,
            customer: order.customer,
            order_id: order.id,
            items: []
          };
        }
        grouped[order.order_number].items.push({
          item: order.item,
          quantity: order.quantity,
          unit: order.unit,
          remark: order.remark,
          supplier_note: order.supplier_note,
          status: order.status,
          id: order.detail_id,
          shipping_date: order.shipping_date
        });
      });
      
      const result = Object.values(grouped);
      console.log('分組後的訂單數據:', result);
      return result;
    },
    isValidForConfirmation() {
      if (!this.selectedOrder) return false;
      return this.selectedOrder.items.every(item => {
        if (item.tempStatus === '已確認') {
          return !!item.tempShippingDate;
        }
        return true;
      });
    },
    uniqueStatuses() {
      const statuses = new Set(this.orders.map(order => order.status));
      return Array.from(statuses).sort();
    },
    totalPages() {
      return Math.ceil(this.groupedOrders.length / this.itemsPerPage);
    },
    paginatedOrders() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.groupedOrders.slice(start, end);
    }
  },
  methods: {
    allItemsPending(items) {
      console.log('檢查訂單項目狀態:', items.map(item => item.status));
      return items.every(item => item.status === '待確認');
    },
    hasConfirmedItems(items) {
      const hasConfirmed = items.some(item => item.status === '已確認');
      const allCancelled = items.every(item => item.status === '已取消');
      return hasConfirmed && !allCancelled;
    },
    async fetchAllOrders() {
      try {
        console.log('開始獲取所有訂單...');
        const response = await axios.post(getApiUrl(API_PATHS.ORDERS_ALL), {}, {
          withCredentials: true
        });

        console.log('API 響應:', response);

        if (response.data.status === 'success') {
          if (!Array.isArray(response.data.data)) {
            console.error('API 返回的數據不是數組格式:', response.data);
            alert('獲取訂單數據格式錯誤');
            return;
          }

          this.orders = response.data.data;
          console.log('所有訂單數據:', this.orders);
          if (this.orders.length > 0) {
            console.log('第一筆訂單的備註:', this.orders[0].remark);
            console.log('第一筆訂單的供應商備註:', this.orders[0].supplier_note);
          }
        } else {
          console.error('API 返回狀態不是 success:', response.data);
          alert('獲取訂單失敗：' + (response.data.message || '未知錯誤'));
        }
      } catch (error) {
        console.error('獲取所有訂單失敗:', error);
        if (error.response) {
          console.error('錯誤響應:', error.response.data);
          console.error('狀態碼:', error.response.status);
        }
        alert('獲取所有訂單失敗：' + (error.response?.data?.message || error.message));
      }
    },
    formatDateTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },
    formatDate(dateString) {
      console.log('Formatting date:', dateString, 'Type:', typeof dateString);
      
      if (!dateString || dateString === 'null' || dateString === 'undefined') {
        console.log('Date is empty or invalid');
        return '待確認';
      }
      
      try {
        const date = new Date(dateString);
        console.log('Parsed date:', date);
        
        if (isNaN(date.getTime())) {
          console.log('Invalid date');
          return '待確認';
        }
        
        const formattedDate = `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`;
        console.log('Formatted date:', formattedDate);
        return formattedDate;
      } catch (error) {
        console.error('Error formatting date:', error);
        return '待確認';
      }
    },
    handleApprove(order) {
      this.selectedOrder = {
        ...order,
        items: order.items.map(item => ({
          ...item,
          tempStatus: '已確認',
          tempShippingDate: item.shipping_date || '',
          tempSupplierNote: item.supplier_note || '',
          isEditing: false,
          tempQuantity: item.quantity,
          originalQuantity: item.quantity
        }))
      };
      this.showConfirmModal = true;
    },
    handleReject(order) {
      this.selectedOrder = {
        ...order,
        items: order.items.map(item => ({
          ...item,
          tempStatus: '已取消',
          tempShippingDate: item.shipping_date || ''
        }))
      };
      this.showConfirmModal = true;
    },
    validateShippingDate(item) {
      if (item.tempStatus === '已確認' && !item.tempShippingDate) {
        alert('核准時必須選擇出貨日期');
      }
    },
    async confirmOrderUpdate() {
      try {
        const adminId = localStorage.getItem('admin_id');
        if (!adminId) {
          this.$router.push('/admin-login');
          return;
        }

        // 1. 使用批量更新API一次性更新所有产品状态
        const productsData = this.selectedOrder.items.map(item => ({
          detail_id: item.id,
          status: item.tempStatus,
          shipping_date: item.tempStatus === '已確認' ? item.tempShippingDate : null,
          supplier_note: item.tempSupplierNote || '',
          quantity: item.tempQuantity
        }));

        await axios.post(getApiUrl(API_PATHS.BATCH_UPDATE_ORDER_STATUS), {
          order_number: this.selectedOrder.orderNumber,
          products: productsData
        }, {
          withCredentials: true
        });

        // 2. 然后更新订单确认状态
        await axios.post(getApiUrl(API_PATHS.UPDATE_ORDER_CONFIRMED), {
          order_number: this.selectedOrder.orderNumber
        }, {
          withCredentials: true
        });

        // 3. 判断整张订单的状态
        const hasConfirmed = this.selectedOrder.items.some(item => item.tempStatus === '已確認');
        const allCancelled = this.selectedOrder.items.every(item => item.tempStatus === '已取消');
        
        // 如果有任何一个产品是已确认，整张订单状态为已确认
        // 只有当所有产品都是已取消时，整张订单状态才是已取消
        const orderStatus = hasConfirmed ? '已確認' : (allCancelled ? '已取消' : '已確認');

        // 4. 记录审核日志 - 包含订单状态变更和产品详细信息
        await axios.post(getApiUrl(API_PATHS.LOG_RECORD), {
          table_name: 'orders',
          operation_type: '審核',  // 使用審核類型
          record_id: this.selectedOrder.order_id,
          old_data: {
            message: `訂單號:${this.selectedOrder.orderNumber}、狀態:待確認`
          },
          new_data: {
            message: {
              order_number: this.selectedOrder.orderNumber,
              status: {
                before: '待確認',
                after: orderStatus
              },
              products: this.selectedOrder.items.map(item => ({
                name: item.item,
                detail_id: item.id,
                quantity: item.tempQuantity,
                shipping_date: item.tempStatus === '已確認' ? item.tempShippingDate : null,
                remark: item.remark || '-',
                supplier_note: item.tempSupplierNote || '-',
                status: item.tempStatus,
                changes: {
                  status: {
                    before: '待確認',
                    after: item.tempStatus
                  },
                  quantity: item.tempQuantity !== item.quantity ? {
                    before: item.quantity,
                    after: item.tempQuantity
                  } : undefined,
                  shipping_date: item.tempStatus === '已確認' && item.tempShippingDate ? {
                    before: item.shipping_date || '待確認',
                    after: item.tempShippingDate
                  } : undefined,
                  supplier_note: item.tempSupplierNote !== item.supplier_note ? {
                    before: item.supplier_note || '-',
                    after: item.tempSupplierNote || '-'
                  } : undefined
                }
              }))
            }
          },
          performed_by: parseInt(adminId),
          user_type: '管理員'
        }, {
          withCredentials: true
        });

        alert('訂單處理完成');
        await this.fetchAllOrders();
      } catch (error) {
        console.error('Error in confirmOrderUpdate:', error);
        alert('處理訂單時發生錯誤：' + (error.response?.data?.message || error.message));
      } finally {
        this.closeConfirmModal();
      }
    },
    closeConfirmModal() {
      this.showConfirmModal = false;
      this.selectedOrder = null;
    },
    exportReport() {
      const headers = [
        "建立日期",
        "客戶",
        "訂單編號",
        "品項",
        "數量",
        "單位",
        "出貨日期",
        "備註",
        "供應商備註",
        "狀態"
      ];

      // 準備數據
      const data = [headers];
      
      // 將訂單數據轉換為扁平結構
      this.groupedOrders.forEach(order => {
        order.items.forEach(item => {
          const row = [
            this.formatDateTime(order.date),
            order.customer,
            order.orderNumber,
            item.item,
            item.quantity,
            item.unit,
            this.formatDate(item.shipping_date),
            item.remark || '-',
            item.supplier_note || '-',
            item.status
          ];
          data.push(row);
        });
      });

      // 創建工作簿和工作表
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet(data);

      // 設置列寬
      ws['!cols'] = [
        { wch: 20 }, // 建立日期
        { wch: 15 }, // 客戶
        { wch: 15 }, // 訂單編號
        { wch: 20 }, // 品項
        { wch: 10 }, // 數量
        { wch: 10 }, // 單位
        { wch: 15 }, // 出貨日期
        { wch: 20 }, // 備註
        { wch: 20 }, // 供應商備註
        { wch: 10 }  // 狀態
      ];

      XLSX.utils.book_append_sheet(wb, ws, "訂單清單");
      XLSX.writeFile(wb, "訂單資料.xlsx");
    },
    resetFilters() {
      this.searchFilters = {
        startDate: '',
        endDate: '',
        company: '',
        orderNumber: '',
        product: '',
        status: ''
      };
      this.currentPage = 1; // 重置時回到第一頁
    },
    handleComplete(order) {
      this.selectedOrder = order;
      this.showCompleteModal = true;
    },
    async confirmComplete() {
      try {
        const adminId = localStorage.getItem('admin_id');
        if (!adminId) {
          this.$router.push('/admin-login');
          return;
        }

        // 獲取所有已確認狀態的產品
        const confirmedProducts = this.selectedOrder.items
          .filter(item => item.status === '已確認');

        // 如果沒有已確認的產品，提示用戶並返回
        if (confirmedProducts.length === 0) {
          alert('沒有可以標記為已出貨的產品');
          this.closeCompleteModal();
          return;
        }

        // 准备所有产品的数据，用于批量更新
        const productsData = confirmedProducts.map(item => ({
          detail_id: item.id,
          status: '已出貨',
          supplier_note: item.supplier_note || ''
        }));

        // 使用批量更新API一次性更新所有产品状态
        await axios.post(getApiUrl(API_PATHS.BATCH_UPDATE_ORDER_STATUS), {
          order_number: this.selectedOrder.orderNumber,
          products: productsData
        }, {
          withCredentials: true
        });

        // 更新订单出货状态
        await axios.post(getApiUrl(API_PATHS.UPDATE_ORDER_SHIPPED), {
          order_number: this.selectedOrder.orderNumber
        }, {
          withCredentials: true
        });

        // 记录审核日志 - 包含订单状态变更和产品详细信息
        await axios.post(getApiUrl(API_PATHS.LOG_RECORD), {
          table_name: 'orders',
          operation_type: '審核',  // 使用審核類型
          record_id: this.selectedOrder.order_id,
          old_data: {
            message: `訂單號:${this.selectedOrder.orderNumber}、狀態:已確認`
          },
          new_data: {
            message: {
              order_number: this.selectedOrder.orderNumber,
              status: {
                before: '已確認',
                after: '已出貨'
              },
              products: confirmedProducts.map(item => ({
                name: item.item,
                detail_id: item.id,
                quantity: item.quantity,
                shipping_date: item.shipping_date,
                remark: item.remark || '-',
                supplier_note: item.supplier_note || '-',
                status: '已出貨',
                changes: {
                  status: {
                    before: '已確認',
                    after: '已出貨'
                  }
                }
              }))
            }
          },
          performed_by: parseInt(adminId),
          user_type: '管理員'
        }, {
          withCredentials: true
        });

        alert('訂單已標記為出貨完成');
        this.fetchAllOrders();
      } catch (error) {
        console.error('Error completing order:', error);
        alert('操作失敗：' + (error.response?.data?.message || error.message));
      } finally {
        this.closeCompleteModal();
      }
    },
    closeCompleteModal() {
      this.showCompleteModal = false;
      this.selectedOrder = null;
    },
    startEdit(item) {
      item.isEditing = true;
      item.tempQuantity = item.quantity;
      item.originalQuantity = item.quantity;
    },
    async saveQuantity(item) {
      try {
        const response = await axios.post(getApiUrl(API_PATHS.UPDATE_ORDER_QUANTITY), {
          order_detail_id: item.id,
          quantity: item.tempQuantity
        }, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          item.quantity = item.tempQuantity;
          item.isEditing = false;
          // 重新獲取訂單數據
          await this.fetchAllOrders();
        } else {
          throw new Error(response.data.message || '更新失敗');
        }
      } catch (error) {
        console.error('Error updating quantity:', error);
        alert('更新數量失敗：' + (error.response?.data?.message || error.message));
        item.tempQuantity = item.originalQuantity;
      }
    },
    cancelEdit(item) {
      item.isEditing = false;
      item.tempQuantity = item.originalQuantity;
    }
  },
  created() {
    this.fetchAllOrders();
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

.completed-text {
  display: inline-block;
  padding: 6px 0;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.modal-content p {
  margin-bottom: 20px;
  color: #666;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-buttons button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.modal-buttons .confirm-btn {
  background-color: #4CAF50;
  color: white;
}

.modal-buttons .cancel-btn {
  background-color: #f44336;
  color: white;
}
</style>

