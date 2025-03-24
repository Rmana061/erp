<!-- 新增訂單方案B -->
<template>
  <body class="customer-mode">
  <div class="container">
    <SideBar menu-type="customer" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ companyName }}您好,<button class="logout-button" @click="logout">登出</button></span>
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
                    <div class="datepicker-container">
                      <Datepicker 
                        v-model="product.shipping_date"
                        :min-date="new Date(getMinShippingDate(product.product_id))"
                        :max-date="new Date(maxDate)"
                        :disabled-dates="getDisabledDatesArray()"
                        :format="formatDate"
                        model-type="yyyy-MM-dd"
                        :enable-time-picker="false"
                        locale="zh"
                        auto-apply
                        required
                        @update:model-value="validateShippingDate(index)"
                        text-input
                        inline-menu
                      />
                    </div>
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
                        {{ formatDate(product.shipping_date) || '未設定' }}
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
import { logoutMixin } from '../mixins/logoutMixin';
import SideBar from '../components/SideBar.vue';
import axios from 'axios';
import { API_PATHS, getApiUrl } from '../config/api';
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

export default {
  name: 'AddOrderPlanB',
  components: {
    SideBar,
    Datepicker
  },
  mixins: [timeMixin, companyMixin, logoutMixin],
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
      currentTime: '',
      lockedDates: []
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
               
               // 对于特殊日期产品，不检查shipping_date
               if (product && product.special_date) {
                 return p.quantity >= product.min_order_qty && 
                        p.quantity <= product.max_order_qty;
               }
               
               return product && 
                      p.quantity >= product.min_order_qty && 
                      p.quantity <= product.max_order_qty &&
                      (p.shipping_date && !this.isDateLocked(p.shipping_date));
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

      // 如果是特殊日期产品，返回空值
      if (product.special_date) {
        return '';
      }

      const today = new Date();
      let minDate = new Date(today);
      minDate.setDate(today.getDate() + (parseInt(product.shipping_time) || 0));
      
      // 检查日期是否被锁定，如果被锁定则延后
      let dateStr = minDate.toISOString().split('T')[0];
      let attempts = 0;
      const maxAttempts = 60; // 防止无限循环，最多尝试60天
      
      // 如果日期被锁定，向后推一天，直到找到未锁定的日期
      while (this.isDateLocked(dateStr) && attempts < maxAttempts) {
        minDate.setDate(minDate.getDate() + 1);
        dateStr = minDate.toISOString().split('T')[0];
        attempts++;
      }
      
      return dateStr;
    },
    async handleProductChange(index) {
      const product = this.orderProducts[index];
      // 确保product_id是整数类型
      if (!product.product_id) return;
      
      const selectedProduct = this.selectedProduct(product.product_id);
      
      if (selectedProduct) {
        console.log('选择了产品:', selectedProduct.name, '产品ID:', product.product_id);
        
        // 检查是否最近订购过
        try {
          const checkResult = await this.checkRecentOrder(product.product_id);
          console.log('重复下单检查结果:', checkResult);
          
          // 使用严格比较，确保布尔值比较正确
          if (checkResult && checkResult.canOrder === false) {
            const message = `重複下單提醒：您在最近${checkResult.limitDays}天內已經訂購過"${selectedProduct.name}"，請聯繫供應商。`;
            console.warn(message);
            alert(message);
            
            // 清空选择
            this.$nextTick(() => {
              product.product_id = '';
            });
            return;
          }
          
          console.log('可以下单此产品');
          
          // 设置最小订购量
          product.quantity = selectedProduct.min_order_qty;
          
          // 设置最早可选日期
          const minShippingDate = this.getMinShippingDate(product.product_id);
          product.shipping_date = minShippingDate;
        } catch (error) {
          console.error('处理产品选择时出错:', error);
          // 错误处理 - 出错时清空选择
          product.product_id = '';
          alert('無法檢查重複訂單，請稍後再試');
        }
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
      if (!product.shipping_date) return;
      
      const minDate = new Date(this.getMinShippingDate(product.product_id));
      const selectedDate = new Date(product.shipping_date);
      
      if (selectedDate < minDate) {
        alert(`根據產品出貨時間，最早可選擇的出貨日期為 ${this.formatDate(minDate)}`);
        product.shipping_date = this.formatDate(minDate);
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
      try {
        if (!this.validateOrder()) {
          return;
        }
        
        // 在提交前再次验证所有产品
        let hasRepeatedProduct = false;
        for (const product of this.orderProducts) {
          if (product.product_id) {
            try {
              const checkResult = await this.checkRecentOrder(product.product_id);
              console.log('提交前检查产品:', product.product_id, '结果:', checkResult);
              
              if (checkResult && checkResult.canOrder === false) {
                const selectedProduct = this.selectedProduct(product.product_id);
                if (selectedProduct) {
                  const message = `重複下單提醒：您在最近${checkResult.limitDays}天內已經訂購過"${selectedProduct.name}"，請聯繫公司。`;
                  alert(message);
                  hasRepeatedProduct = true;
                  break;
                }
              }
            } catch (error) {
              console.error('提交前检查产品出错:', error);
              alert('检查重复订单时出错，请稍后再试');
              return;
            }
          }
        }
        
        if (hasRepeatedProduct) {
          return; // 如果有重复产品，停止提交
        }

        const orderData = this.prepareOrderData();
        console.log('Submitting order data:', orderData);
        
        const response = await axios.post(getApiUrl(API_PATHS.CREATE_ORDER), orderData, {
          withCredentials: true
        });

        console.log('Create order response:', response.data);

        if (response.data.status === 'success') {
          // 準備日誌信息
          const customerId = localStorage.getItem('customer_id');
          
          // 确保产品信息中包含客户备注和供应商备注
          const productsList = orderData.products.map(product => {
            const selectedProd = this.selectedProduct(product.product_id);
            return {
              name: selectedProd.name,
              quantity: product.product_quantity,
              shipping_date: this.formatDate(product.shipping_date) || '待確認',
              remark: product.remark || '-',
              supplier_note: product.supplier_note || '-'
            };
          });
          
          console.log('Products for log message:', productsList);
          
          // 构建日志消息
          const logMessage = JSON.stringify({
            order_number: this.generatedOrderNumber,
            status: '待確認',
            products: productsList
          });

          const logData = {
            table_name: 'orders',
            operation_type: '新增',
            record_id: response.data.order_id || response.data.data?.id || null,
            new_data: {
              message: logMessage
            },
            performed_by: parseInt(customerId),
            user_type: '客戶'
          };

          // 输出日志消息到控制台，用于调试
          console.log('Generated log message:', logMessage);

          // 如果沒有 order_id，使用其他方式獲取
          if (!logData.record_id) {
            try {
              // 嘗試通過訂單號查詢訂單ID
              const orderResponse = await axios.post(getApiUrl(API_PATHS.ORDERS), {
                order_number: this.generatedOrderNumber
              }, {
                withCredentials: true
              });
              if (orderResponse.data.status === 'success' && orderResponse.data.data?.length > 0) {
                logData.record_id = orderResponse.data.data[0].id;
              }
            } catch (error) {
              console.error('Error fetching order id:', error);
            }
          }

          if (logData.record_id) {
            console.log('Preparing to send log data:', logData);

            // 記錄操作日誌
            try {
              const logResponse = await axios.post(getApiUrl(API_PATHS.LOG_OPERATION), logData, {
                withCredentials: true
              });
              console.log('Log operation response:', logResponse.data);
            } catch (logError) {
              console.error('Error logging operation:', logError);
              console.error('Log error details:', logError.response?.data);
            }
          }

          alert('訂單提交成功！');
          this.$router.push('/order-record');
        } else {
          throw new Error(response.data.message || '訂單提交失敗');
        }
      } catch (error) {
        console.error('Error submitting order:', error);
        if (error.response?.status === 401) {
          alert('請重新登入');
          this.$router.push('/customer-login');
          return;
        }
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

        const response = await axios.get(getApiUrl(API_PATHS.CUSTOMER_INFO), {
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
        const customerId = localStorage.getItem('customer_id');
        const companyName = localStorage.getItem('company_name');
        
        if (!customerId || !companyName) {
          console.log('Missing customer information');
          localStorage.setItem('redirect_after_login', '/add-order');
          this.$router.push('/customer-login');
          return;
        }

        console.log('Fetching products for customer:', customerId);
        const response = await axios.post(getApiUrl(API_PATHS.PRODUCTS), {
          type: 'customer',
          customer_id: customerId,
          company_name: companyName
        }, {
          withCredentials: true,
          headers: {
            'X-Customer-ID': customerId,
            'X-Company-Name': companyName
          }
        });

        console.log('Products response:', response.data);

        if (response.data.status === 'success') {
          console.log('Raw product data:', response.data.data);
          this.availableProducts = response.data.data.map(product => ({
            id: product.id,
            name: product.name,
            min_order_qty: product.min_order_qty || 1,
            max_order_qty: product.max_order_qty || 9999,
            unit: product.product_unit || 'kg',
            shipping_time: product.shipping_time || 0,
            special_date: product.special_date || false
          }));
          console.log('Processed available products:', this.availableProducts);
        } else {
          throw new Error(response.data.message || '獲取產品列表失敗');
        }
      } catch (error) {
        console.error('Error fetching products:', error);
        if (error.response) {
          console.error('Error response:', error.response.data);
          if (error.response.status === 401) {
            // 如果认证失败，清除缓存并重定向到登录页面
            localStorage.removeItem('customer_id');
            this.$router.push('/customer-login');
            return;
          }
        }
        this.availableProducts = [];
        alert('獲取產品列表失敗：' + (error.response?.data?.message || error.message));
      }
    },
    formatDate(date) {
      if (!date) return '';
      const d = new Date(date);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    isDateLocked(date) {
      if (!date) return false;
      if (!this.lockedDates || this.lockedDates.length === 0) return false;
      
      const dateStr = typeof date === 'string' ? date : this.formatDate(date);
      console.log('检查日期是否锁定:', dateStr);
      
      return this.lockedDates.some(lockedDate => {
        let lockedDateStr = '';
        
        if (typeof lockedDate === 'string') {
          lockedDateStr = this.formatDate(new Date(lockedDate));
        } else if (lockedDate && lockedDate.locked_date) {
          lockedDateStr = this.formatDate(new Date(lockedDate.locked_date));
        }
        
        return lockedDateStr === dateStr;
      });
    },
    async fetchLockedDates() {
      try {
        const customerId = localStorage.getItem('customer_id');
        const companyName = localStorage.getItem('company_name');
        
        if (!customerId || !companyName) {
          return;
        }
        
        console.log('开始获取锁定日期...');
        const response = await axios.post(getApiUrl(API_PATHS.LOCKED_DATES), {}, {
          withCredentials: true,
          headers: {
            'X-Customer-ID': customerId,
            'X-Company-Name': companyName
          }
        });
        
        console.log('锁定日期API响应:', response.data);
        
        if (response.data.status === 'success') {
          // 处理API返回的数据格式
          if (Array.isArray(response.data.data)) {
            this.lockedDates = response.data.data;
            console.log('成功获取锁定日期:', this.lockedDates);
          } else {
            console.error('锁定日期数据格式不正确:', response.data.data);
            this.lockedDates = [];
          }
        } else {
          console.error('获取锁定日期失败:', response.data.message);
          this.lockedDates = [];
        }
      } catch (error) {
        console.error('Error fetching locked dates:', error);
        if (error.response) {
          console.error('Error response:', error.response.data);
        }
        this.lockedDates = [];
      }
    },
    getDisabledDatesArray() {
      console.log('锁定日期数组:', this.lockedDates);
      if (!this.lockedDates || this.lockedDates.length === 0) {
        return [];
      }
      
      // 处理可能的不同数据格式
      return this.lockedDates.map(date => {
        if (typeof date === 'string') {
          return new Date(date);
        } else if (date && date.locked_date) {
          return new Date(date.locked_date);
        }
        return null;
      }).filter(date => date !== null);
    },
    validateOrder() {
      if (!this.isFormValid) {
        alert('請檢查訂單資料是否完整');
        return false;
      }
      
      const customerId = localStorage.getItem('customer_id');
      if (!customerId) {
        alert('未找到客戶ID，請重新登入');
        return false;
      }
      
      return true;
    },
    prepareOrderData() {
      const customerId = localStorage.getItem('customer_id');
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
            remark: product.remark ? product.remark.trim() : '',
            supplier_note: ''
          };
        })
      };

      console.log('Prepared order data:', JSON.stringify(orderData, null, 2));
      return orderData;
    },
    async checkRecentOrder(productId) {
      try {
        const customerId = localStorage.getItem('customer_id');
        const companyName = localStorage.getItem('company_name');
        
        if (!customerId || !companyName) {
          return { canOrder: true, limitDays: 0 };
        }
        
        console.log('检查重复订单 - 产品ID:', productId, '客户ID:', customerId);
        
        // 修改请求，确保数据格式正确
        const response = await axios.post(getApiUrl(API_PATHS.CHECK_RECENT_ORDER), {
          customer_id: parseInt(customerId),
          product_id: parseInt(productId)
        }, {
          withCredentials: true,
          headers: {
            'X-Customer-ID': customerId,
            'X-Company-Name': companyName
          }
        });
        
        console.log('重复订单检查响应:', response.data);
        
        if (response.data.status === 'success') {
          if (response.data.data) {
            // 正確解析新的API格式
            return {
              canOrder: response.data.data.can_order,
              limitDays: response.data.data.limit_days || 0
            };
          } else {
            // 處理可能的空數據情況
            console.warn('API返回成功但無數據');
            return { canOrder: true, limitDays: 0 };
          }
        } else {
          console.warn('重复订单检查API返回格式不正确:', response.data);
          return { canOrder: true, limitDays: 0 };
        }
      } catch (error) {
        console.error('检查重复订单时出错:', error);
        
        if (error.response) {
          console.error('错误详情:', error.response.data);
          
          // 特別處理枚舉值錯誤 - 訂單狀態問題
          if (error.response.status === 500 && error.response.data?.message && 
              (error.response.data.message.includes('invalid input value for enum order_status') || 
               error.response.data.message.includes('已出貨'))) {
            console.warn('訂單狀態枚舉錯誤，繼續處理');
            // 當數據庫枚舉值出錯時，預設允許下單
            return { canOrder: true, limitDays: 0 };
          }
        }
        
        // 其他錯誤情況，默認允許下單但在控制台提示錯誤
        // 這樣即使API有問題，用戶也能繼續使用系統
        console.warn('重複下單檢查失敗，默認允許下單');
        return { canOrder: true, limitDays: 0 };
      }
    }
  },
  created() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
    this.fetchCompanyInfo();
    console.log('Component created, fetching products...');
    this.fetchProducts();
    this.fetchLockedDates();
  },
  async mounted() {
    // 验证登录状态
    const customerId = localStorage.getItem('customer_id');
    const companyName = localStorage.getItem('company_name');
    
    if (!customerId || !companyName) {
      console.log('Not logged in, redirecting to login page');
      localStorage.setItem('redirect_after_login', '/add-order');
      this.$router.push('/customer-login');
      return;
    }
    
    try {
      // 验证会话是否有效
      const sessionCheck = await axios.post(getApiUrl(API_PATHS.CUSTOMER_INFO), {
        customer_id: customerId
      }, {
        withCredentials: true,
        headers: {
          'X-Customer-ID': customerId,
          'X-Company-Name': companyName
        }
      });
      
      if (sessionCheck.data.status !== 'success') {
        throw new Error('Session invalid');
      }
      
      // 获取数据
      await Promise.all([
        this.fetchProducts(),
        this.fetchLockedDates()
      ]);
      
      document.title = '合揚訂單系統';
    } catch (error) {
      console.error('Session verification failed:', error);
      localStorage.setItem('redirect_after_login', '/add-order');
      this.$router.push('/customer-login');
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 日期选择器样式覆盖 */
.dp__main {
  width: 100%;
  max-width: 100%;
}

.dp__menu {
  z-index: 1000 !important;
}

.dp__outer_menu {
  position: absolute !important;
}

.dp__input {
  padding: 8px !important;
  border: 1px solid #ccc !important;
  border-radius: 4px !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.datepicker-container {
  position: relative;
  width: 100%;
}
</style>
