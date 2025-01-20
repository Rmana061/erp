<!-- 新增訂單方案B -->
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
        <div class="scrollable-content">
          <div class="page-header">
            <h2>新增訂單</h2>
            <p class="order-number">訂單號：{{ generatedOrderNumber }}</p>
          </div>

          <div class="order-form">
            <div class="form-group" v-for="(product, index) in orderProducts" :key="index">
              <div class="input-group">
                <div class="product-header">
                  <button v-if="index > 0" class="remove-btn" @click="removeProduct(index)">移除</button>
                </div>
                <div class="product-select">
                  <select 
                    :id="'product' + (index + 1)" 
                    v-model="product.product_id"
                    @change="handleProductChange(index)">
                    <option value="">請選擇產品</option>
                    <option v-for="item in availableProducts" 
                            :key="item.id" 
                            :value="item.id">
                      {{ item.name }}
                    </option>
                  </select>
                </div>
                <div class="quantity-input">
                  <div class="quantity-control">
                    <input 
                      type="number" 
                      v-model.number="product.quantity"
                      :min="selectedProduct(product.product_id)?.min_order_qty || 1"
                      :max="selectedProduct(product.product_id)?.max_order_qty || 9999"
                      @input="validateQuantity(index)">
                    <span class="unit">{{ selectedProduct(product.product_id)?.unit || 'kg' }}</span>
                  </div>
                  <div class="quantity-hint" v-if="selectedProduct(product.product_id)">
                    最小訂購量: {{ selectedProduct(product.product_id).min_order_qty }}
                    最大訂購量: {{ selectedProduct(product.product_id).max_order_qty }}
                  </div>
                </div>
                <div class="date-input">
                  <label :for="'shipping-date' + index">出貨日期：</label>
                  <template v-if="selectedProduct(product.product_id)?.special_date">
                    <div class="special-date-notice">請和供應商確認日期</div>
                  </template>
                  <template v-else>
                    <input 
                      type="date" 
                      :id="'shipping-date' + index"
                      v-model="product.shipping_date"
                      :min="getMinShippingDate(product.product_id)"
                      :max="maxDate"
                      @change="validateShippingDate(index)"
                      required>
                    <div class="shipping-hint" v-if="product.product_id && selectedProduct(product.product_id)">
                      <div>最早出貨日期：{{ getMinShippingDate(product.product_id) }}</div>
                      <div class="shipping-time">（出貨時間：{{ selectedProduct(product.product_id).shipping_time || 0 }}天）</div>
                    </div>
                  </template>
                </div>
                <div class="remark-input">
                  <label :for="'remark' + index">備註：</label>
                  <textarea 
                    :id="'remark' + index"
                    v-model="product.remark"
                    rows="2"
                    placeholder="請輸入備註（選填）"
                    maxlength="200">
                  </textarea>
                  <div class="char-count">{{ product.remark.length }}/200</div>
                </div>
              </div>
            </div>
            
            <div class="add-product">
              <button @click="addProduct" :disabled="orderProducts.length >= 10">
                + 新增品項
              </button>
              <span class="hint" v-if="orderProducts.length >= 10">
                最多可新增 10 個品項
              </span>
            </div>
            
            <div class="order-summary" v-if="hasProducts">
              <h3>訂單摘要</h3>
              <div class="summary-items">
                <div v-for="(product, index) in orderProducts" :key="index">
                  <template v-if="product.product_id">
                    {{ selectedProduct(product.product_id)?.name }} - 
                    {{ product.quantity }} {{ selectedProduct(product.product_id)?.unit || 'kg' }}
                    <div class="summary-detail">
                      出貨日期：
                      <template v-if="selectedProduct(product.product_id)?.special_date">
                        請和供應商確認日期
                      </template>
                      <template v-else>
                        {{ product.shipping_date || '未設定' }}
                      </template>
                      <div v-if="product.remark" class="summary-remark">
                        備註：{{ product.remark }}
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
            
            <div class="button-group">
              <button 
                class="submit-btn" 
                @click="submitOrder"
                :disabled="!isFormValid">
                提交訂單
              </button>
              <button class="cancel-btn" @click="cancelOrder">取消</button>
            </div>
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
  name: 'AddOrderPlanB',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  data() {
    return {
      orderProducts: [{
        product_id: '',
        quantity: 1,
        shipping_date: '',
        remark: ''
      }],
      availableProducts: [],
      generatedOrderNumber: this.generateOrderNumber(),
      currentTime: ''
    };
  },
  computed: {
    hasProducts() {
      console.log('Available products count:', this.availableProducts.length);
      return this.orderProducts.some(p => p.product_id && p.quantity > 0);
    },
    isFormValid() {
      return this.orderProducts.some(p => p.product_id && p.quantity > 0) &&
             this.orderProducts.every(p => {
               if (!p.product_id) return true;
               const product = this.selectedProduct(p.product_id);
               return product && 
                      p.quantity >= product.min_order_qty && 
                      p.quantity <= product.max_order_qty;
             });
    },
    minDate() {
      const today = new Date();
      return today.toISOString().split('T')[0];
    },
    maxDate() {
      const today = new Date();
      const maxDate = new Date();
      maxDate.setMonth(today.getMonth() + 3); // 最多可選擇三個月內的日期
      return maxDate.toISOString().split('T')[0];
    }
  },
  methods: {
    generateOrderNumber() {
      const date = new Date();
      const year = date.getFullYear().toString().slice(-2);
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
      return `T${year}${month}${day}${random}`;
    },
    selectedProduct(productId) {
      return this.availableProducts.find(p => p.id === productId);
    },
    getMinShippingDate(productId) {
      const product = this.selectedProduct(productId);
      if (!product) {
        return this.minDate;
      }

      const today = new Date();
      const minDate = new Date(today);
      minDate.setDate(today.getDate() + (parseInt(product.shipping_time) || 0));
      return minDate.toISOString().split('T')[0];
    },
    handleProductChange(index) {
      const product = this.orderProducts[index];
      const selectedProduct = this.selectedProduct(product.product_id);
      if (selectedProduct) {
        // 设置最小订购量
        product.quantity = selectedProduct.min_order_qty;
        
        // 设置最早可选日期
        const minShippingDate = this.getMinShippingDate(product.product_id);
        product.shipping_date = minShippingDate;
      }
    },
    validateQuantity(index) {
      const product = this.orderProducts[index];
      const selectedProduct = this.selectedProduct(product.product_id);
      if (!selectedProduct) return;
      
      if (product.quantity < selectedProduct.min_order_qty) {
        product.quantity = selectedProduct.min_order_qty;
      } else if (product.quantity > selectedProduct.max_order_qty) {
        product.quantity = selectedProduct.max_order_qty;
      }
    },
    validateShippingDate(index) {
      const product = this.orderProducts[index];
      const minDate = this.getMinShippingDate(product.product_id);
      
      if (product.shipping_date && product.shipping_date < minDate) {
        alert(`根據產品出貨時間，最早可選擇的出貨日期為 ${minDate}`);
        product.shipping_date = minDate;
      }
    },
    addProduct() {
      if (this.orderProducts.length < 10) {
        this.orderProducts.push({
          product_id: '',
          quantity: 1,
          shipping_date: '',
          remark: ''
        });
      }
    },
    removeProduct(index) {
      this.orderProducts.splice(index, 1);
    },
    async submitOrder() {
      if (!this.isFormValid) return;
      
      try {
        // 获取当前客户ID
        const customerId = localStorage.getItem('customer_id');
        if (!customerId) {
          throw new Error('未找到客戶ID，請重新登入');
        }

        // 过滤掉未选择产品的项目
        const validProducts = this.orderProducts.filter(p => p.product_id && p.quantity > 0);
        
        // 准备订单数据
        const orderData = {
          order_number: this.generatedOrderNumber,
          customer_id: parseInt(customerId),
          products: validProducts.map(product => {
            const selectedProd = this.selectedProduct(product.product_id);
            return {
              product_id: product.product_id,
              product_quantity: product.quantity,
              product_unit: selectedProd.unit,
              order_status: '待確認',
              shipping_date: selectedProd.special_date ? null : product.shipping_date,
              remark: product.remark.trim()
            };
          })
        };

        // 发送订单到后端
        const response = await axios.post('http://localhost:5000/api/orders', orderData, {
          withCredentials: true
        });

        console.log('訂單提交成功:', response.data);
        alert('訂單已成功提交');
        this.$router.push('/order-system');
      } catch (error) {
        console.error('提交訂單失敗:', error);
        alert('提交訂單失敗：' + (error.response?.data?.message || error.message));
      }
    },
    cancelOrder() {
      if (confirm('確定要取消訂單嗎？已填寫的內容將會遺失。')) {
        this.$router.push('/order-system');
      }
    },
    async fetchCompanyInfo() {
      try {
        const customerId = localStorage.getItem('customer_id');
        console.log('Customer ID from localStorage:', customerId);
        
        if (!customerId) {
          console.log('No customer_id found in localStorage');
          this.$router.push('/customer-login');
          return;
        }

        const cachedUserInfo = sessionStorage.getItem('userInfo');
        if (cachedUserInfo) {
          const userInfo = JSON.parse(cachedUserInfo);
          console.log('Cached user info:', userInfo);
          if (userInfo && userInfo.company_name) {
            this.companyName = userInfo.company_name;
            return;
          }
        }

        const response = await axios.get('http://localhost:5000/api/customer/info', {
          withCredentials: true
        });
        
        console.log('Company info response:', response.data);
        
        if (response.data.status === 'success') {
          this.companyName = response.data.data.company_name;
          sessionStorage.setItem('userInfo', JSON.stringify(response.data.data));
        } else {
          throw new Error(response.data.message || '获取用户信息失败');
        }
      } catch (error) {
        console.error('Error in fetchCompanyInfo:', error);
        if (error.response) {
          console.error('Error response:', error.response.data);
        }
        this.companyName = '客戶';
      }
    },
    async fetchProducts() {
      try {
        console.log('Fetching products...');
        // 先从 sessionStorage 获取用户信息
        const cachedUserInfo = sessionStorage.getItem('userInfo');
        if (!cachedUserInfo) {
          console.log('No cached user info found');
          this.$router.push('/customer-login');
          return;
        }

        const userInfo = JSON.parse(cachedUserInfo);
        console.log('User info from cache:', userInfo);
        
        if (!userInfo.viewable_products) {
          console.log('No viewable products found');
          this.availableProducts = [];
          return;
        }

        // 获取可见产品的详细信息
        const response = await axios.get(`http://localhost:5000/api/products/viewable?ids=${userInfo.viewable_products}`, {
          withCredentials: true
        });

        console.log('Products response:', response.data);

        if (response.data.status === 'success') {
          console.log('Raw product data:', response.data.data);
          this.availableProducts = response.data.data.map(product => {
            console.log(`Processing product ${product.id}:`, product);
            return {
              id: product.id,
              name: product.name,
              min_order_qty: product.min_order_qty || 1,
              max_order_qty: product.max_order_qty || 9999,
              unit: product.product_unit || 'kg',
              shipping_time: product.shipping_time || 0,
              special_date: product.special_date || false
            };
          });
          console.log('Processed available products:', this.availableProducts);
        }
      } catch (error) {
        console.error('Error fetching products:', error);
        if (error.response) {
          console.error('Error response:', error.response.data);
          if (error.response.status === 401) {
            // 如果认证失败，清除缓存并重定向到登录页面
            sessionStorage.removeItem('userInfo');
            localStorage.removeItem('customer_id');
            this.$router.push('/customer-login');
            return;
          }
        }
        this.availableProducts = [];
      }
    }
  },
  created() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
    this.fetchCompanyInfo();
    console.log('Component created, fetching products...');
    this.fetchProducts();
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

.special-date-notice {
  color: #e74c3c;
  font-size: 0.9em;
  padding: 8px;
  background-color: #fdeaea;
  border-radius: 4px;
  margin-top: 4px;
  text-align: center;
}

/* 所有其他樣式已移至 unified-base */
</style>
