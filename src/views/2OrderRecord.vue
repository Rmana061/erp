<!-- 訂貨紀錄 -->
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
          <h2>訂貨紀錄</h2>
        </div>
        
        <div class="scrollable-content">
          <!-- 添加搜索框 -->
          <div class="search-panel compact">
            <div class="search-form-row">
              <div class="search-form-item">
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="搜索訂單號、日期或產品名稱..."
                  class="search-input"
                >
              </div>
            </div>
          </div>

          <div class="table-container">
            <table class="order-table">
              <thead>
                <tr>
                  <th>訂單編號</th>
                  <th>建立日期</th>
                  <th>產品</th>
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
                  <tr v-for="(product, productIndex) in order.products" :key="order.order_number + '-' + productIndex"
                      :class="{ 
                        'first-product': productIndex === 0,
                        'approved': product.order_status === '已確認',
                        'rejected': product.order_status === '已取消',
                        'shipped': product.order_status === '已出貨'
                      }">
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
                    <td>{{ product.remark || '-' }}</td>
                    <td>{{ product.supplier_note || '-' }}</td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <button @click="currentPage--" :disabled="currentPage === 1">上一页</button>
            <span>第 {{ currentPage }} 页</span>
            <button @click="currentPage++" :disabled="currentPage * ordersPerPage >= orders.length">下一页</button>
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
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'OrderRecord',
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
      ordersPerPage: 10,
      searchQuery: ''
    };
  },
  computed: {
    filteredOrders() {
      if (!this.searchQuery) {
        return this.orders;
      }
      
      const searchLower = this.searchQuery.toLowerCase().trim();
      
      return this.orders.filter(order => {
        // 搜索订单号（支持部分匹配）
        const orderNumberMatch = order.order_number.toLowerCase().includes(searchLower);
        
        // 搜索日期（支持多种格式）
        const createdDate = new Date(order.created_at);
        const dateStr = this.formatDate(order.created_at).toLowerCase();
        const shortDateStr = `${createdDate.getFullYear()}/${String(createdDate.getMonth() + 1).padStart(2, '0')}/${String(createdDate.getDate()).padStart(2, '0')}`.toLowerCase();
        const dateMatch = dateStr.includes(searchLower) || shortDateStr.includes(searchLower);
        
        // 搜索产品名称
        const productMatch = order.products.some(product => 
          product.product_name.toLowerCase().includes(searchLower)
        );
        
        return orderNumberMatch || dateMatch || productMatch;
      });
    },
    
    paginatedOrders() {
      const start = (this.currentPage - 1) * this.ordersPerPage;
      return this.filteredOrders.slice(start, start + this.ordersPerPage);
    },
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
      return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },
    async fetchOrders() {
      try {
        const customerId = localStorage.getItem('customer_id');
        console.log('Fetching orders for customer:', customerId);

        const response = await axios.get(getApiUrl(API_PATHS.ORDERS), {
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
    document.title = '訂貨紀錄';
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


/* 搜索框样式 */
.search-panel.compact {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.search-form-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-form-item {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #4CAF50;
  outline: none;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.search-input::placeholder {
  color: #999;
}

/* 所有其他樣式已移至 unified-base */
</style>