<!-- 產品一覽 -->
<template>
  <body class="customer-mode">
  <div class="container">
    <SideBar menu-type="customer" />
      <div class="main-content">
        <div class="header">
          <span>Hi {{ companyName }}您好,</span>
          <span>{{ currentTime }}</span>
        </div>

        <div class="content-wrapper">
          <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
              placeholder="搜索產品..."
            class="search-input" 
            >
        </div>
        <div class="scrollable-content">
      <div class="product-grid">
            <div v-for="product in filteredProducts" :key="product.id" class="card product-card">
          <div class="product-image">
            <img 
              :src="product.image_url" 
              :alt="product.name"
              @click="showLargeImage(product.image_url)"
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
                <a v-if="product.dm_url" 
                   :href="product.dm_url" 
                   target="_blank" 
                     class="btn btn-primary">
                  查看 DM
                </a>
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
import SideBar from '../components/SideBar.vue';
import axios from 'axios';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'ProductList',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  data() {
    return {
      username: 'Customer',
      products: [],
      showModal: false,
      selectedImage: '',
      searchQuery: ''
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
    async fetchProducts() {
      try {
        const customerId = localStorage.getItem('customer_id');
        if (!customerId) {
          console.log('No customer_id found');
          this.$router.push('/customer-login');
          return;
        }

        console.log('Fetching products for customer:', customerId);
        const response = await axios.post(getApiUrl(API_PATHS.PRODUCTS), {
          type: 'customer',
          customer_id: customerId
        }, {
          withCredentials: true
        });
            
        console.log('Products response:', response.data);
        if (response.data.status === 'success') {
          this.products = response.data.data.map(product => ({
            id: product.id,
            name: product.name,
            description: product.description,
            image_url: product.image_url,
            dm_url: product.dm_url,
            min_order_qty: product.min_order_qty,
            max_order_qty: product.max_order_qty,
            unit: product.unit || product.product_unit,
            shipping_time: product.shipping_time,
            created_at: product.created_at,
            updated_at: product.updated_at
          }));
          console.log('Processed products:', this.products);
        } else {
          throw new Error(response.data.message || '獲取產品列表失敗');
        }
      } catch (error) {
        console.error('Error fetching products:', error);
        console.error('Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        });
        
        if (error.response?.status === 401) {
          this.$router.push('/customer-login');
        } else {
          alert('獲取產品列表失敗：' + (error.response?.data?.message || error.message));
        }
      }
    },
    showLargeImage(imageUrl) {
      this.selectedImage = imageUrl;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    }
  },
  created() {
    this.fetchProducts();
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
