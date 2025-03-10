<!-- 訂貨系統 -->
<template>
  <body class="customer-mode">
  <div class="container">
    <SideBar menu-type="customer" />
    
    <div class="main-content">
      <div class="header">
        <span>Hi {{ companyName }}您好,</span>
        <span id="current-time">{{ currentTime }}</span>
      </div>
      
      <div class="content-wrapper">
          <h2>訂貨系統</h2>
          <p>以下為過去兩週的訂貨紀錄</p>
        <div class="action-buttons">
          <button class="action-button" @click="navigateToAddOrder">+ 新增訂單</button>
          <button class="action-button" @click="handleCancelOrder" :disabled="!selectedOrder">
            - 取消訂單
          </button>
        </div>

        <div class="scrollable-content">
          <div class="table-container">
            <table class="order-table">
              <thead>
                <tr>
                  <th>建立日期</th>
                  <th>訂單編號</th>
                  <th>品項</th>
                  <th>數量</th>
                  <th>單位</th>
                  <th>狀態</th>
                  <th>出貨日期</th>
                  <th>備註</th>
                  <th>供應商備註</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="order in paginatedOrders" :key="order.order_number">
                  <tr v-for="(product, productIndex) in order.products" 
                      :key="order.order_number + '-' + productIndex"
                      :class="{ 
                        'first-product': productIndex === 0,
                        'selected-order': order.order_number === selectedOrder,
                        'cancelable-order': canCancelOrder(order),
                        'approved': product.order_status === '已確認',
                        'rejected': product.order_status === '已取消',
                        'shipped': product.order_status === '已出貨'
                      }"
                      @click="handleOrderClick(order)">
                    <td>{{ productIndex === 0 ? formatDate(order.created_at) : '' }}</td>
                    <td>{{ productIndex === 0 ? order.order_number : '' }}</td>
                    <td>{{ product.product_name }}</td>
                    <td>{{ product.product_quantity }}</td>
                    <td>{{ product.product_unit }}</td>
                    <td>
                      <span class="status-badge" :class="product.order_status">
                        {{ product.order_status }}
                      </span>
                    </td>
                    <td>{{ product.shipping_date || '待確認' }}</td>
                    <td>{{ product.remark || '-' }}</td>
                    <td>{{ product.supplier_note || '-' }}</td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <button @click="currentPage--" :disabled="currentPage === 1">上一页</button>
            <span>第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
            <button @click="currentPage++" :disabled="currentPage >= totalPages">下一页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 取消訂單確認對話框 -->
    <div class="modal" v-if="showCancelModal">
      <div class="modal-content">
        <h3>取消訂單確認</h3>
        <p>確定要取消訂單 {{ selectedOrder }} 嗎？</p>
        <p class="warning-text">此操作無法撤銷！</p>
        <div class="modal-buttons">
          <button class="confirm-btn" @click="confirmCancelOrder">確認取消</button>
          <button class="cancel-btn" @click="showCancelModal = false">返回</button>
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import { timeMixin } from '../mixins/timeMixin';
import { companyMixin } from '../mixins/companyMixin';
import SideBar from '../components/SideBar.vue';
import axios from 'axios';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'OrderSystem',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  data() {
    return {
      orders: [],
      selectedOrder: null,
      showCancelModal: false,
      currentPage: 1,
      ordersPerPage: 10
    };
  },
  computed: {
    paginatedOrders() {
      const start = (this.currentPage - 1) * this.ordersPerPage;
      return this.orders.slice(start, start + this.ordersPerPage);
    },
    totalPages() {
      return Math.ceil(this.orders.length / this.ordersPerPage);
    },
  },
  methods: {
    navigateToAddOrder() {
      this.$router.push('/add-order-plan-b');
    },
    canCancelOrder(order) {
      return order.products.every(product => product.order_status === '待確認');
    },
    handleOrderClick(order) {
      if (this.canCancelOrder(order)) {
        this.selectedOrder = this.selectedOrder === order.order_number ? null : order.order_number;
      }
    },
    handleCancelOrder() {
      if (this.selectedOrder) {
        this.showCancelModal = true;
      }
    },
    async confirmCancelOrder() {
      try {
        const customerId = localStorage.getItem('customer_id');
        if (!customerId) {
          alert('請重新登入');
          this.$router.push('/customer-login');
          return;
        }

        // 取消订单
        const response = await axios.post(getApiUrl(API_PATHS.CANCEL_ORDER), {
          order_number: this.selectedOrder
        }, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          // 從列表中移除已取消的訂單
          this.orders = this.orders.filter(order => order.order_number !== this.selectedOrder);
          alert('訂單已成功取消');
        } else {
          throw new Error(response.data.message || '取消訂單失敗');
        }
      } catch (error) {
        console.error('取消訂單時發生錯誤:', error);
        alert('取消訂單失敗：' + (error.response?.data?.message || error.message));
      } finally {
        this.showCancelModal = false;
        this.selectedOrder = null;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },
    async fetchOrders() {
      try {
        const customerId = localStorage.getItem('customer_id');
        console.log('Fetching orders for customer:', customerId);

        const response = await axios.post(getApiUrl(API_PATHS.ORDERS), {
          customer_id: customerId
        }, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          const allOrders = response.data.data;
          const twoWeeksAgo = new Date();
          twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
          this.orders = allOrders.filter(order => new Date(order.created_at) >= twoWeeksAgo);
        }
      } catch (error) {
        console.error('Error fetching orders:', error);
        if (error.response?.status === 401) {
          this.$router.push('/customer-login');
        }
      }
    }
  },
  created() {
    this.fetchOrders();
  },
  mounted() {
    document.title = '訂貨系統';
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

.table-container {
  margin-top: 20px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.order-table {
  width: 100%;
  border-collapse: collapse;
}

.order-table th,
.order-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.order-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.cancelable-order {
  cursor: pointer;
}

.cancelable-order:hover {
  background-color: #f5f5f5;
}

.selected-order {
  background-color: #e8f0fe !important;
}

.first-product td {
  border-top: 2px solid #ddd;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  display: inline-block;
}


/* 彈出視窗樣式 */
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

.warning-text {
  color: #dc3545;
  margin: 15px 0;
  font-weight: bold;
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

.confirm-btn {
  background-color: #dc3545;
  color: white;
}

.confirm-btn:hover {
  background-color: #c82333;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

/* 所有其他樣式已移至 unified-base */
</style>