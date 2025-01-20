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
        <div class="page-header">
          <h2>訂貨系統</h2>
        </div>

        <div class="action-buttons">
          <button class="action-button" @click="navigateToAddOrder">+ 新增訂單</button>
          <button class="action-button" @click="cancelOrder">- 取消訂單</button>
        </div>

        <div class="scrollable-content">
          <div class="table-container">
            <table class="order-table">
              <thead>
                <tr>
                  <th>訂單編號</th>
                  <th>建立日期</th>
                  <th>品項</th>
                  <th>數量</th>
                  <th>單位</th>
                  <th>狀態</th>
                  <th>出貨日期</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="order in orders" :key="order.order_number">
                  <tr v-for="(product, productIndex) in order.products" :key="order.order_number + '-' + productIndex"
                      :class="{ 'first-product': productIndex === 0 }">
                    <td>{{ productIndex === 0 ? order.order_number : '' }}</td>
                    <td>{{ productIndex === 0 ? formatDate(order.created_at) : '' }}</td>
                    <td>{{ product.product_name }}</td>
                    <td>{{ product.product_quantity }}</td>
                    <td>{{ product.product_unit }}</td>
                    <td>
                      <span class="status-badge" :class="product.order_status">
                        {{ product.order_status }}
                      </span>
                    </td>
                    <td>{{ product.shipping_date || '待確認' }}</td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
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

export default {
  name: 'OrderSystem',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  data() {
    return {
      orders: []
    };
  },
  methods: {
    navigateToAddOrder() {
      this.$router.push('/add-order-plan-b');
    },
    cancelOrder() {
      alert('取消訂單功能尚未實現');
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`;
    },
    async fetchOrders() {
      try {
        const customerId = localStorage.getItem('customer_id');
        console.log('Fetching orders for customer:', customerId);

        const response = await axios.get('http://localhost:5000/api/orders', {
          params: {
            customer_id: customerId
          },
          withCredentials: true
        });

        console.log('Raw response:', response);

        if (response.data.status === 'success') {
          this.orders = response.data.data;
          console.log('Processed orders:', this.orders);
        } else {
          console.warn('Response status is not success:', response.data);
        }
      } catch (error) {
        console.error('Error fetching orders:', error);
        if (error.response) {
          console.error('Error response:', error.response.data);
        }
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

.order-table tr:hover {
  background-color: #f5f5f5;
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

.status-badge.待確認 {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.待出貨 {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.已完成 {
  background-color: #cce5ff;
  color: #004085;
}

.status-badge.已取消 {
  background-color: #f8d7da;
  color: #721c24;
}

/* 所有其他樣式已移至 unified-base */
</style>