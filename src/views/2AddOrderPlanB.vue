<!-- 新增訂單方案B -->
<template>
  <body class="customer-mode">
  <div class="container">
    <SideBar menu-type="customer" />
    <div class="main-content">
      <div class="header">
        <span>Hi A公司您好,</span>
        <span id="current-time">{{ currentTime }}</span>
      </div>
      
      <div class="content-wrapper">
        <div class="page-header">
          <h2>新增訂單</h2>
          <p class="order-number">訂單號：{{ generatedOrderNumber }}</p>
        </div>

        <div class="order-form">
          <div class="form-group" v-for="(product, index) in orderProducts" :key="index">
            <div class="input-group">
              <div class="product-header">
                <label :for="'product' + (index + 1)">品項 {{ index + 1 }}</label>
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
                <input 
                  type="date" 
                  :id="'shipping-date' + index"
                  v-model="product.shipping_date"
                  :min="minDate"
                  :max="maxDate"
                  required>
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
                    出貨日期：{{ product.shipping_date || '未設定' }}
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
  </body>
</template>

<script>
import { timeMixin } from '../mixins/timeMixin';
import SideBar from '../components/SideBar.vue';

export default {
  name: 'AddOrderPlanB',
  components: {
    SideBar
  },
  mixins: [timeMixin],
  data() {
    return {
      orderProducts: [{
        product_id: '',
        quantity: 1,
        shipping_date: '',
        remark: ''
      }],
      availableProducts: [
        { id: 1, name: '漂白水', min_order_qty: 5, max_order_qty: 100, unit: 'kg' },
        { id: 2, name: '硫酸', min_order_qty: 10, max_order_qty: 200, unit: 'kg' },
        { id: 3, name: '鹽酸', min_order_qty: 8, max_order_qty: 150, unit: 'kg' }
      ],
      generatedOrderNumber: this.generateOrderNumber()
    };
  },
  computed: {
    hasProducts() {
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
    handleProductChange(index) {
      const product = this.orderProducts[index];
      const selectedProduct = this.selectedProduct(product.product_id);
      if (selectedProduct) {
        product.quantity = selectedProduct.min_order_qty;
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
        const orderData = {
          order_number: this.generatedOrderNumber,
          products: this.orderProducts.filter(p => p.product_id && p.quantity > 0)
            .map(p => ({
              product_id: p.product_id,
              quantity: p.quantity,
              unit: this.selectedProduct(p.product_id).unit,
              shipping_date: p.shipping_date,
              remark: p.remark.trim()
            })),
          status: '待確認'
        };
        
        console.log('提交訂單:', orderData);
        alert('訂單已提交');
        this.$router.push('/order-system');
      } catch (error) {
        console.error('提交訂單失敗:', error);
        alert('提交訂單失敗，請稍後重試');
      }
    },
    cancelOrder() {
      if (confirm('確定要取消訂單嗎？已填寫的內容將會遺失。')) {
        this.$router.push('/order-system');
      }
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
