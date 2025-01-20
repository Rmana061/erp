<!-- 今日訂單 -->
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
          <button class="export-btn" @click="exportOrders">
            <i class="fas fa-file-export"></i> 報表匯出
          </button>
        </div>

        <div class="scrollable-content">
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>序號</th>
                  <th>建立日期</th>
                  <th>客戶</th>
                  <th>訂單編號</th>
                  <th>品項</th>
                  <th>數量</th>
                  <th>單位</th>
                  <th>出貨日期</th>
                  <th>備註</th>
                  <th>狀態</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(order, orderIndex) in groupedOrders" :key="order.orderNumber">
                  <tr v-for="(item, itemIndex) in order.items" 
                      :key="order.orderNumber + '-' + itemIndex"
                      :class="{ 
                        'first-product': itemIndex === 0,
                        'approved': item.status === '已確認', 
                        'rejected': item.status === '已取消' 
                      }">
                    <td>{{ itemIndex === 0 ? orderIndex + 1 : '' }}</td>
                    <td>{{ itemIndex === 0 ? formatDateTime(order.date) : '' }}</td>
                    <td>{{ itemIndex === 0 ? order.customer : '' }}</td>
                    <td>{{ itemIndex === 0 ? order.orderNumber : '' }}</td>
                    <td>{{ item.item }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ item.unit }}</td>
                    <td>{{ formatDate(item.shipping_date) }}</td>
                    <td>{{ item.note }}</td>
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
    groupedOrders() {
      const grouped = {};
      this.orders.forEach(order => {
        if (!grouped[order.orderNumber]) {
          grouped[order.orderNumber] = {
            orderNumber: order.orderNumber,
            date: order.date,
            customer: order.customer,
            items: []
          };
        }
        grouped[order.orderNumber].items.push({
          item: order.item,
          quantity: order.quantity,
          unit: order.unit,
          note: order.note,
          status: order.status,
          id: order.id,
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
    }
  },
  methods: {
    async fetchTodayOrders() {
      try {
        const response = await axios.get('http://localhost:5000/api/orders/today', {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          this.orders = response.data.data;
          console.log('Today orders raw data:', response.data.data);
          
          // 檢查每個訂單的 shipping_date
          this.orders.forEach(order => {
            console.log(`Order ${order.orderNumber} shipping_date:`, order.shipping_date);
          });
        }
      } catch (error) {
        console.error('Error fetching today orders:', error);
        alert('獲取今日訂單失敗：' + (error.response?.data?.message || error.message));
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
          axios.post('http://localhost:5000/api/orders/update-status', {
            order_id: item.id,
            status: item.tempStatus,
            shipping_date: item.tempStatus === '已確認' ? item.tempShippingDate : null
          }, {
            withCredentials: true
          })
        );

        await Promise.all(updatePromises);
        alert('訂單處理完成');
        this.fetchTodayOrders();
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
    }
  },
  created() {
    this.fetchTodayOrders();
  }
};
</script>

<style scoped>
@import '../assets/styles/unified-base.css';

.table-container {
  margin-top: 20px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  display: inline-block;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.approve-btn {
  background-color: #28a745;
  color: white;
}

.approve-btn:hover {
  background-color: #218838;
}

/* 確認對話框樣式 */
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
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  width: 400px;
  text-align: center;
}

.modal-content h3 {
  margin-bottom: 20px;
  color: #333;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.modal-buttons button {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.confirm-btn.approve {
  background-color: #28a745;
  color: white;
}

.confirm-btn.reject {
  background-color: #dc3545;
  color: white;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.notification {
  margin-top: 20px;
  padding: 10px;
  background-color: #e9ecef;
  border-radius: 4px;
  text-align: center;
  color: #666;
}

/* 已處理訂單的樣式 */
tr.approved {
  background-color: #f8fff8;
}

tr.rejected {
  background-color: #fff8f8;
}

.shipping-date-selector {
  margin: 20px 0;
  text-align: left;
}

.shipping-date-selector label {
  display: block;
  margin-bottom: 8px;
  color: #333;
}

.shipping-date-selector input[type="date"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.date-hint {
  color: #dc3545;
  font-size: 0.9em;
  margin-top: 4px;
}

.confirm-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.first-product td {
  border-top: 2px solid #ddd;
}

.order-review {
  width: 80%;
  max-width: 800px;
}

.order-items {
  margin: 20px 0;
  max-height: 400px;
  overflow-y: auto;
}

.review-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.review-table th,
.review-table td {
  padding: 10px;
  border: 1px solid #ddd;
}

.review-table th {
  background-color: #f8f9fa;
}

.review-table input[type="date"],
.review-table select {
  width: 100%;
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.review-table select {
  background-color: white;
}

.review-table input[type="date"]:disabled,
.review-table select:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

/* 所有其他樣式已移至 unified-base */
</style>

