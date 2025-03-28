<!-- 訂貨紀錄 -->
<template>
  <body class="customer-mode">
  <div class="container order-record">
    <SideBar menu-type="customer" />
    
    <div class="main-content">
      <div class="header">
        <span>Hi {{ companyName }}您好,<button class="logout-button" @click="logout">登出</button></span>
        <span>{{ currentTime }}</span>
      </div>
      
      <div class="content-wrapper">
          <h2>訂貨紀錄</h2>
        <div class="scrollable-content">
          <!-- 添加搜索框 -->
          <div class="search-panel compact">
            <div class="search-form-row">
              <!-- 文本搜索 -->
              <div class="search-form-item">
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="搜索訂單號或產品名稱..."
                  class="search-input"
                >
              </div>
              
              <!-- 日期範圍搜索 -->
              <div class="search-form-item date-range-field">
                <div class="date-range-wrapper">
                  <input 
                    type="date" 
                    v-model="startDate" 
                    class="date-field"
                    :max="endDate || undefined"
                  >
                  <span class="date-separator">至</span>
                  <input 
                    type="date" 
                    v-model="endDate" 
                    class="date-field"
                    :min="startDate || undefined"
                  >
                </div>
              </div>
              
              <!-- 重置按鈕 -->
              <div class="search-form-item">
                <button @click="resetFilters" class="reset-btn">重置</button>
              </div>
            </div>
          </div>

          <div class="table-container">
            <table class="order-table">
              <thead>
                <tr>
                  <th>建立日期</th>
                  <th>訂單編號</th>
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
import { logoutMixin } from '../mixins/logoutMixin';
import SideBar from '../components/SideBar.vue';
import axios from 'axios';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'OrderRecord',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin, logoutMixin],
  data() {
    return {
      orders: [],
      selectedOrder: null,
      showCancelModal: false,
      currentPage: 1,
      ordersPerPage: 10,
      searchQuery: '',
      startDate: '',
      endDate: ''
    };
  },
  computed: {
    filteredOrders() {
      let result = this.orders;
      
      // 文本搜索过滤
      if (this.searchQuery) {
        const searchLower = this.searchQuery.toLowerCase().trim();
        
        result = result.filter(order => {
          // 搜索订单号（支持部分匹配）
          const orderNumberMatch = order.order_number.toLowerCase().includes(searchLower);
          
          // 搜索产品名称
          const productMatch = order.products.some(product => 
            product.product_name.toLowerCase().includes(searchLower)
          );
          
          return orderNumberMatch || productMatch;
        });
      }
      
      // 日期范围过滤
      if (this.startDate || this.endDate) {
        result = result.filter(order => {
          const orderDate = new Date(order.created_at);
          orderDate.setHours(0, 0, 0, 0); // 重置时间部分以便比较日期
          
          if (this.startDate && this.endDate) {
            // 转换为Date对象以进行比较
            const start = new Date(this.startDate);
            start.setHours(0, 0, 0, 0);
            
            const end = new Date(this.endDate);
            end.setHours(23, 59, 59, 999); // 设置为当天结束时间
            
            return orderDate >= start && orderDate <= end;
          } else if (this.startDate) {
            const start = new Date(this.startDate);
            start.setHours(0, 0, 0, 0);
            return orderDate >= start;
          } else if (this.endDate) {
            const end = new Date(this.endDate);
            end.setHours(23, 59, 59, 999);
            return orderDate <= end;
          }
          
          return true;
        });
      }
      
      return result;
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

        const response = await axios.post(getApiUrl(API_PATHS.ORDERS), {
          customer_id: customerId
        }, {
          withCredentials: true
        });

        console.log('Raw response:', response);

        if (response.data.status === 'success') {
          // 確保 response.data.data 是陣列
          const ordersData = Array.isArray(response.data.data) ? response.data.data : [];
          console.log('獲取到的訂單數據:', ordersData);
          
          // 過濾掉無效的訂單數據
          this.orders = ordersData.filter(order => {
            if (!order) {
              console.warn('發現空訂單數據');
              return false;
            }
            
            // 確保訂單有必要的屬性
            if (!order.products || !Array.isArray(order.products)) {
              console.warn('訂單缺少產品數據:', order);
              return false;
            }
            
            // 確保每個產品都有必要的屬性
            order.products = order.products.filter(product => {
              if (!product) {
                console.warn('發現空產品數據');
                return false;
              }
              return true;
            });
            
            return order.products.length > 0;
          });
          
          console.log('處理後的訂單數據:', this.orders);
        } else {
          console.warn('Response status is not success:', response.data);
          this.orders = [];
        }
      } catch (error) {
        console.error('Error fetching orders:', error);
        if (error.response) {
          console.error('Error response:', error.response.data);
        }
        if (error.response?.status === 401) {
          this.$router.push('/customer-login');
        }
        this.orders = [];
      }
    },
    resetFilters() {
      this.searchQuery = '';
      this.startDate = '';
      this.endDate = '';
    }
  },
  created() {
    this.fetchOrders();
  },
  mounted() {
    document.title = '合揚訂單系統';
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';
</style>