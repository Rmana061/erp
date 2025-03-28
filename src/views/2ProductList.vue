<!-- 產品一覽 -->
<template>
  <body class="customer-mode">
  <div class="container">
    <SideBar menu-type="customer" />
      <div class="main-content">
        <div class="header">
          <span>Hi {{ companyName }}您好,<button class="logout-button" @click="logout">登出</button></span>
          <span>{{ currentTime }}</span>
        </div>

        <div class="content-wrapper">
          <h2>產品一覽</h2>
          <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
              placeholder="搜索產品..."
            class="search-input" 
            >
        </div>
        <div class="scrollable-content">
      <div v-if="loading" class="loading">
        加載中...
      </div>
      <div v-else-if="error" class="error-message">
        {{ error }}
        <div v-if="isAuthError" class="login-redirect">
          <button @click="redirectToLogin" class="action-button">重新登錄</button>
        </div>
      </div>
      <div v-else-if="products.length === 0" class="no-products">
        暫無產品
      </div>
      <div v-else class="product-grid">
            <div v-for="product in filteredProducts" :key="product.id" class="card product-card">
          <div class="product-image">
            <img 
              :src="product.image_url" 
              :alt="product.name"
              @click="showLargeImage(product.image_url)"
              @error="handleImageError($event)"
            >
          </div>
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <div class="product-details">
              <p class="description">{{ product.description }}</p>
              <div class="detail-row">
                <span class="label">最小訂購量：</span>
                    <span class="value">{{ product.min_order_qty }} {{ product.unit }}</span>
              </div>
              <div class="detail-row">
                <span class="label">最大訂購量：</span>
                    <span class="value">{{ product.max_order_qty }} {{ product.unit }}</span>
              </div>
              <div class="detail-row">
                <span class="label">出貨時間：</span>
                    <span class="value">{{ product.shipping_time }} 天</span>
              </div>
            </div>
            <div class="product-actions">
                <button 
                  class="table-button" 
                  @click="openDM(product.dm_url, product.name)">
                  查看 DM
                </button>
              </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 圖片預覽模態框 -->
    <div v-if="showModal" class="modal" @click="closeModal">
      <img :src="selectedImage" alt="Large preview" class="modal-content">
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
  name: 'ProductList',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin, logoutMixin],
  data() {
    return {
      username: 'Customer',
      products: [],
      showModal: false,
      selectedImage: '',
      searchQuery: '',
      loading: true,
      error: null,
      retryCount: 0,
      isAuthError: false,
      defaultImage: '../../../no-image.png'
    };
  },
  computed: {
    filteredProducts() {
      return this.products.filter(product => {
        return product.name.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    }
  },
  methods: {
    // 检查并恢复会话信息
    checkAndRestoreSession() {
      // 从localStorage获取会话信息
      let customerId = localStorage.getItem('customer_id');
      let companyName = localStorage.getItem('company_name');
      
      // 如果localStorage中没有，尝试从sessionStorage恢复
      if (!customerId || !companyName) {
        console.log('本地存储中未找到完整会话信息，尝试从会话存储恢复');
        try {
          const userInfo = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
          if (userInfo.customer_id && userInfo.company_name) {
            console.log('从会话存储恢复会话信息:', userInfo);
            localStorage.setItem('customer_id', userInfo.customer_id);
            localStorage.setItem('company_name', userInfo.company_name);
            customerId = userInfo.customer_id;
            companyName = userInfo.company_name;
          }
        } catch (e) {
          console.error('恢复会话时出错:', e);
        }
      }
      
      return { customerId, companyName };
    },
    
    async fetchProducts() {
      this.loading = true;
      this.error = null;
      this.isAuthError = false;
      
      try {
        // 检查并尝试恢复会话
        const { customerId, companyName } = this.checkAndRestoreSession();
        
        console.log('当前会话状态:', {
          customerId,
          companyName,
          isLoggedIn: !!customerId && !!companyName
        });
        
        if (!customerId || !companyName) {
          console.log('未找到用户信息，重定向到登录页面');
          this.error = '會話已過期，請重新登錄';
          this.isAuthError = true;
          localStorage.setItem('redirect_after_login', this.$route.fullPath);
          return;
        }

        console.log('获取客户编号为', customerId, '的产品列表');
        
        // 对公司名称进行编码
        const encodedCompanyName = encodeURIComponent(companyName);
        
        // 首先获取客户信息以获取可见产品列表
        const customerResponse = await axios.post(getApiUrl(API_PATHS.CUSTOMER_DETAIL(customerId)), {}, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
            'X-Customer-ID': customerId,
            'X-Company-Name': encodedCompanyName
          }
        });

        if (customerResponse.data.status !== 'success') {
          throw new Error('無法獲取客戶資料');
        }

        const viewableProducts = customerResponse.data.data.viewable_products
          ? customerResponse.data.data.viewable_products.split(',').map(id => parseInt(id.trim()))
          : [];

        console.log('客戶可見產品ID列表:', viewableProducts);
        
        // 获取产品列表
        const response = await axios.post(getApiUrl(API_PATHS.PRODUCTS), {
          type: 'customer',
          customer_id: customerId,
          company_name: companyName,
          timestamp: new Date().getTime()
        }, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
            'X-Customer-ID': customerId,
            'X-Requested-With': 'XMLHttpRequest',
            'X-Company-Name': encodedCompanyName
          }
        });
            
        console.log('产品数据响应:', response.data);
        
        if (response.data.status === 'success') {
          // 过滤只显示可见的产品
          this.products = response.data.data
            .filter(product => viewableProducts.includes(product.id))
            .map(product => ({
              id: product.id,
              name: product.name,
              description: product.description,
              image_url: product.image_url || this.defaultImage,
              dm_url: product.dm_url,
              dm_original_filename: product.dm_original_filename || '',
              min_order_qty: product.min_order_qty,
              max_order_qty: product.max_order_qty,
              unit: product.unit || product.product_unit,
              shipping_time: product.shipping_time,
              created_at: product.created_at,
              updated_at: product.updated_at
            }));
          console.log('處理後的產品數據:', this.products);
        } else {
          throw new Error(response.data.message || '獲取產品列表失敗');
        }
      } catch (error) {
        console.error('获取产品失败:', error);
        console.error('错误详情:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        });
        
        if (error.response?.status === 401) {
          // 如果是401错误，尝试重新登录
          this.error = '會話已過期，請重新登錄';
          this.isAuthError = true;
          
          // 保存当前URL以便登录后返回
          localStorage.setItem('redirect_after_login', this.$route.fullPath);
          // 清除登录信息
          localStorage.removeItem('customer_id');
          localStorage.removeItem('company_name');
        } else if (this.retryCount < 2) {
          // 尝试自动重试
          this.retryCount++;
          console.log(`第${this.retryCount}次重试获取产品列表...`);
          setTimeout(() => {
            this.fetchProducts();
          }, 1000);
        } else {
          this.error = '獲取產品列表失敗：' + (error.response?.data?.message || error.message);
        }
      } finally {
        this.loading = false;
      }
    },
    
    redirectToLogin() {
      // 保存当前页面路径并跳转到登录页面
      localStorage.setItem('redirect_after_login', this.$route.fullPath);
      this.$router.push('/customer-login');
    },
    
    showLargeImage(imageUrl) {
      this.selectedImage = imageUrl;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    openDM(url, productName) {
      if (!url) {
        alert(`${productName} 此產品尚無DM`);
        return;
      }
      
      // 从产品列表中查找对应的产品
      const product = this.products.find(p => p.dm_url === url);
      let originalFilename = '';
      
      // 依次嘗試獲取原始檔名
      if (product) {
        originalFilename = product.dm_original_filename || 
                          product.original_dm_filename || 
                          '';
      }
      
      console.log('打開DM，URL:', url);
      console.log('原始文件名:', originalFilename);
      
      // 檢查文件類型
      const isPdf = originalFilename.toLowerCase().endsWith('.pdf');
      
      if (url.startsWith('http') && originalFilename) {
        // 創建下載/預覽URL
        const downloadUrl = getApiUrl(`/api/azure-blob/download?url=${encodeURIComponent(url)}&filename=${encodeURIComponent(originalFilename)}`);
        
        // 針對PDF文件，使用新視窗打開以便預覽
        // 針對其他文件，使用下載方式
        window.open(downloadUrl, '_blank');
      } else if (url.startsWith('http')) {
        // 如果是Azure URL但沒有原始文件名，直接打開
        window.open(url, '_blank', 'noopener,noreferrer');
      } else {
        // 本地文件，添加域名
        const baseUrl = window.location.origin;
        const fullUrl = `${baseUrl}${url}`;
        window.open(fullUrl, '_blank', 'noopener,noreferrer');
      }
    },
    handleImageError(event) {
      // 當圖片載入失敗時，使用預設圖片
      event.target.src = this.defaultImage;
    }
  },
  created() {
    this.fetchProducts();
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

.loading {
  text-align: center;
  padding: 30px;
  font-size: 18px;
  color: #555;
}

.error-message {
  text-align: center;
  padding: 30px;
  color: #e74c3c;
  font-size: 16px;
  background-color: #fdf7f7;
  border-radius: 8px;
  margin: 20px;
}

.login-redirect {
  margin-top: 15px;
}

.no-products {
  text-align: center;
  padding: 50px;
  color: #7f8c8d;
  font-size: 18px;
}

/* 所有其他樣式已移至 unified-base */
</style>
