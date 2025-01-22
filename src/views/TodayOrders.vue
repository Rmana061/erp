<!-- 待確認訂單 -->
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
        <div class="page-header">
          <h2>待確認訂單</h2>
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

        <div class="scrollable-content">
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
                        'rejected': item.status === '已取消' 
                      }">
                    <td>{{ itemIndex === 0 ? formatDateTime(order.date) : '' }}</td>
                    <td>{{ itemIndex === 0 ? order.customer : '' }}</td>
                    <td>{{ itemIndex === 0 ? order.orderNumber : '' }}</td>
                    <td>{{ item.item }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ item.unit }}</td>
                    <td>{{ formatDate(item.shipping_date) }}</td>
                    <td>{{ item.remark || '-' }}</td>
                    <td>{{ item.supplier_note || '-' }}</td>
                    <td>
                      <span class="status-badge" :class="item.status">{{ item.status }}</span>
                    </td>
                    <td>
                      <div class="action-buttons" v-if="itemIndex === 0 && allItemsPending(order.items)">
                        <button class="approve-btn" @click="handleApprove(order)">
                          審核
                        </button>
                      </div>
                      <span v-else-if="itemIndex === 0">已處理</span>
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
        </div>
        
        <div class="notification">
          結果會透過LINE發送
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
                <td>{{ item.quantity }}</td>
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
                    :disabled="item.tempStatus === '已取消'"
                    placeholder="請輸入供應商備註">
                </td>
                <td>
                  <select v-model="item.tempStatus">
                    <option value="待確認">待確認</option>
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
  </div>
  </body>
</template>

<script>
import { timeMixin } from '../mixins/timeMixin';
import { adminMixin } from '../mixins/adminMixin';
import SideBar from '../components/SideBar.vue';
import axios from 'axios';
import { API_BASE_URL, API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'TodayOrders',
  components: {
    SideBar
  },
  mixins: [timeMixin, adminMixin],
  data() {
    return {
      orders: [],
      showConfirmModal: false,
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
      this.filteredOrders.forEach(order => {
        if (!grouped[order.order_number]) {
          grouped[order.order_number] = {
            orderNumber: order.order_number,
            date: order.date,
            customer: order.customer,
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
      return Object.values(grouped);
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
    async fetchPendingOrders() {
      try {
        console.log('開始獲取待確認訂單...');
        const response = await axios.get(getApiUrl(API_PATHS.PENDING_ORDERS), {
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
          console.log('待確認訂單數據:', this.orders);
          if (this.orders.length > 0) {
            console.log('第一筆訂單的備註:', this.orders[0].remark);
            console.log('第一筆訂單的供應商備註:', this.orders[0].supplier_note);
          }
        } else {
          console.error('API 返回狀態不是 success:', response.data);
          alert('獲取訂單失敗：' + (response.data.message || '未知錯誤'));
        }
      } catch (error) {
        console.error('獲取待確認訂單失敗:', error);
        if (error.response) {
          console.error('錯誤響應:', error.response.data);
          console.error('狀態碼:', error.response.status);
        }
        alert('獲取待確認訂單失敗：' + (error.response?.data?.message || error.message));
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
    allItemsPending(items) {
      return items.every(item => item.status === '待確認');
    },
    handleApprove(order) {
      this.selectedOrder = {
        ...order,
        items: order.items.map(item => ({
          ...item,
          tempStatus: '已確認',
          tempShippingDate: item.shipping_date || ''
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
        const updatePromises = this.selectedOrder.items.map(item => 
          axios.post(getApiUrl(API_PATHS.UPDATE_ORDER_STATUS), {
            order_id: item.id,
            status: item.tempStatus,
            shipping_date: item.tempStatus === '已確認' ? item.tempShippingDate : null
          }, {
            withCredentials: true
          })
        );

        await Promise.all(updatePromises);
        alert('訂單處理完成');
        this.fetchPendingOrders();
      } catch (error) {
        console.error('Error updating order:', error);
        alert('訂單處理失敗：' + (error.response?.data?.message || error.message));
      } finally {
        this.closeConfirmModal();
      }
    },
    closeConfirmModal() {
      this.showConfirmModal = false;
      this.selectedOrder = null;
    },
    exportOrders() {
      // TODO: 實現匯出功能
      alert('匯出功能尚未實現');
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
    }
  },
  created() {
    this.fetchPendingOrders();
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';
</style>

