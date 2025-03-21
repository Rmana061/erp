<!-- 新增客戶 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,<button class="logout-button" @click="logout">登出</button></span>
        <span>{{ currentTime }}</span>
      </div>
      
      <h2>{{ isEditing ? '編輯客戶' : '新增客戶' }}</h2>
      <div class="scrollable-content">
        <form @submit.prevent="submitCustomer">
          <div class="form-container">
            <div class="form-group">
              <label>公司名稱：</label>
              <input type="text" v-model="newCustomer.companyName" placeholder="（管理員自填）">
            </div>
            <div class="form-group">
              <label>帳號：</label>
              <input type="text" v-model="newCustomer.account" placeholder="（管理員自填）">
            </div>
            <div class="form-group">
              <label>密碼：</label>
              <input type="password" v-model="newCustomer.password" placeholder="（管理員自填）">
            </div>
            <div class="form-group">
              <label>可購產品：</label>
              <div class="product-selection-container">
                <div class="product-search">
                  <input 
                    type="text" 
                    v-model="productSearchQuery" 
                    placeholder="搜索產品名稱"
                    class="product-search-input"
                  >
                </div>
                <div class="checkbox-grid">
                  <label 
                    v-for="(product, index) in filteredProducts" 
                    :key="index" 
                    class="custom-checkbox product-checkbox"
                  >
                    <input 
                      type="checkbox" 
                      v-model="newCustomer.selectedProducts" 
                      :value="product.value"
                    >
                    <span class="checkmark"></span>
                    <span :title="product.name" class="product-name">{{ product.name }}</span>
                  </label>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>LINE帳號設置：</label>
              <div class="line-setup-container">
                <div class="line-note">
                  注意：客戶需要透過掃描QR碼自行綁定LINE帳號。<br>
                  此欄位僅供顯示已綁定帳號。請在建立客戶後指導客戶如何進行綁定。
                </div>
                <div v-if="isEditing && (lineUsers.length > 0 || lineGroups.length > 0)" class="line-accounts-summary">
                  <div v-if="lineUsers.length > 0" class="line-summary-section">
                    <h4>已綁定個人帳號 ({{ lineUsers.length }})</h4>
                    <ul class="line-account-list">
                      <li v-for="(user, index) in lineUsers" :key="'user-'+index">
                        {{ user.user_name || '未知用戶' }}
                      </li>
                    </ul>
                  </div>
                  <div v-if="lineGroups.length > 0" class="line-summary-section">
                    <h4>已綁定群組 ({{ lineGroups.length }})</h4>
                    <ul class="line-account-list">
                      <li v-for="(group, index) in lineGroups" :key="'group-'+index">
                        {{ group.group_name || '未命名群組' }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>聯絡人：</label>
              <input type="text" v-model="newCustomer.contactPerson" placeholder="請輸入聯絡人姓名">
            </div>
            <div class="form-group">
              <label>電話：</label>
              <input type="tel" v-model="newCustomer.phone" placeholder="請輸入聯絡電話">
            </div>
            <div class="form-group">
              <label>Email：</label>
              <input type="email" v-model="newCustomer.email" placeholder="請輸入電子郵件地址">
            </div>
            <div class="form-group">
              <label>地址：</label>
              <input type="text" v-model="newCustomer.address" placeholder="請輸入完整地址">
            </div>
            <div class="form-group">
              <label>重複下單限制：</label>
              <input type="number" v-model="newCustomer.reorderLimitDays" min="0" placeholder="0表示無限制" class="short-input">
              <span class="field-hint">設置客戶在多少天內不能重複下單相同產品，0表示無限制</span>
            </div>
            <div class="form-group">
              <label>備註：</label>
              <textarea v-model="newCustomer.notes" placeholder="請輸入其他相關備註"></textarea>
            </div>
            <div class="button-group">
              <button type="submit" class="submit-btn">確認</button>
              <button type="button" class="cancel-btn" @click="$router.go(-1)">取消</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import axios from 'axios';
import SideBar from '../components/SideBar.vue';
import { adminMixin } from '../mixins/adminMixin';
import { API_PATHS } from '../config/api';
import axiosInstance from '../config/axios';
import { timeMixin } from '../mixins/timeMixin';
import { logoutMixin } from '../mixins/logoutMixin';

export default {
  name: 'AddCustomer',
  mixins: [adminMixin, timeMixin, logoutMixin],
  components: {
    SideBar
  },
  data() {
    return {
      isMenuOpen: false,
      currentTime: '',
      isEditing: false,
      productSearchQuery: '',
      newCustomer: {
        companyName: '',
        account: '',
        password: '',
        selectedProducts: [],
        contactPerson: '',
        phone: '',
        email: '',
        address: '',
        reorderLimitDays: 2,
        notes: ''
      },
      products: [],
      editingId: null,
      lineUsers: [],
      lineGroups: []
    };
  },
  computed: {
    filteredProducts() {
      if (!this.productSearchQuery) {
        return this.products;
      }
      
      const query = this.productSearchQuery.toLowerCase().trim();
      return this.products.filter(product => 
        product.name.toLowerCase().includes(query)
      );
    }
  },
  async created() {
    // 检查是否是编辑模式
    const customerId = this.$route.query.id;
    if (customerId) {
      this.isEditing = true;
      this.editingId = customerId;
      await this.fetchCustomerDetails(customerId);
    }
    
    await this.fetchProducts();
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
      document.body.style.overflow = this.isMenuOpen ? 'hidden' : '';
    },
    closeMenu() {
      this.isMenuOpen = false;
      document.body.style.overflow = '';
    },
    async fetchCustomerDetails(customerId) {
      try {
        const response = await axiosInstance.post(
          API_PATHS.CUSTOMER_DETAIL(customerId)
        );

        if (response.data.status === 'success') {
          const customerData = response.data.data;
          this.newCustomer = {
            companyName: customerData.company_name || '',
            account: customerData.username || '',
            password: '', // 密码不回填
            selectedProducts: customerData.viewable_products ? customerData.viewable_products.split(',').map(p => p.trim()).filter(p => p !== '') : [],
            contactPerson: customerData.contact_person || '',
            phone: customerData.phone || '',
            email: customerData.email || '',
            address: customerData.address || '',
            reorderLimitDays: customerData.reorder_limit_days || 2,
            notes: customerData.remark || ''
          };
          
          // 獲取LINE用戶和群組資料
          this.lineUsers = customerData.line_users || [];
          this.lineGroups = customerData.line_groups || [];
        } else {
          throw new Error(response.data.message || '獲取客戶資料失敗');
        }
      } catch (error) {
        console.error('Error fetching customer details:', error);
        if (error.response?.status === 401) {
          this.$router.push('/admin-login');
          return;
        }
        alert('獲取客戶資料失敗：' + (error.response?.data?.message || error.message));
      }
    },
    async submitCustomer() {
      try {
        // 表单验证
        const requiredFields = {
          companyName: '公司名稱',
          account: '帳號',
          contactPerson: '聯絡人',
          phone: '電話',
          email: 'Email',
          address: '地址'
        };

        // 如果不是编辑模式，添加密码验证
        if (!this.isEditing) {
          requiredFields.password = '密碼';
        }

        for (const [field, label] of Object.entries(requiredFields)) {
          if (!this.newCustomer[field]) {
            alert(`請填寫${label}`);
            return;
          }
        }

        // 准备发送到后端的数据
        const customerData = {
          username: this.newCustomer.account,
          company_name: this.newCustomer.companyName,
          contact_person: this.newCustomer.contactPerson,
          phone: this.newCustomer.phone,
          email: this.newCustomer.email,
          address: this.newCustomer.address,
          viewable_products: this.newCustomer.selectedProducts.join(','),
          reorder_limit_days: this.newCustomer.reorderLimitDays,
          remark: this.newCustomer.notes || ''
        };

        // 如果不是编辑模式或有填写新密码，则添加密码字段
        if (!this.isEditing || this.newCustomer.password) {
          customerData.password = this.newCustomer.password;
        }

        let response;
        if (this.isEditing) {
          // 编辑现有客户时，获取原始数据与当前数据的对比
          customerData.id = this.editingId;
          
          // 获取原始客户数据
          const originalDataResponse = await axiosInstance.post(
            API_PATHS.CUSTOMER_DETAIL(this.editingId)
          );
          
          if (originalDataResponse.data.status === 'success') {
            // 将原始数据添加到请求中，以便后端可以比较变更
            customerData.original_data = originalDataResponse.data.data;
          }
          
          // 发送更新请求
          response = await axiosInstance.put(API_PATHS.CUSTOMER_UPDATE, customerData);
        } else {
          // 新增客户
          response = await axiosInstance.post(API_PATHS.CUSTOMER_ADD, customerData);
        }

        if (response.data.status === 'success') {
          alert(this.isEditing ? '客戶更新成功' : '客戶新增成功');
          this.$router.push('/customer-management');
        } else {
          throw new Error(response.data.message || '操作失敗');
        }
      } catch (error) {
        console.error('Error submitting customer:', error);
        if (error.response?.status === 401) {
          this.$router.push('/admin-login');
          return;
        }
        alert(error.response?.data?.message || '操作失敗，請稍後再試');
      }
    },
    updateCurrentTime() {
      const now = new Date();
      const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        weekday: 'long', 
        hour: '2-digit', 
        minute: '2-digit', 
        hour12: false 
      };
      this.currentTime = now.toLocaleString('zh-TW', options)
        .replace(/\//g, '/')
        .replace('星期', ' 星期')
        .replace(/(\d+):(\d+)/, '$1:$2');
    },
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
    updateCustomer() {
      alert('更新功能尚未實現');
    },
    async fetchProducts() {
      try {
        const response = await axiosInstance.post(API_PATHS.PRODUCTS, {
          type: 'admin'
        });

        if (response.data.status === 'success') {
          this.products = response.data.data.map(product => ({
            name: product.name,
            value: product.id.toString()
          }));
        } else {
          throw new Error(response.data.message || '獲取產品列表失敗');
        }
      } catch (error) {
        console.error('Error fetching products:', error);
        if (error.response?.status === 401) {
          this.$router.push('/admin-login');
          return;
        }
        alert('獲取產品列表失敗：' + (error.response?.data?.message || error.message));
      }
    }
  },
  async mounted() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
    document.title = '合揚訂單後端系統';
    await this.fetchAdminInfo();
    await this.fetchProducts();
  },
  watch: {
    $route() {
      this.closeMenu();
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 保留僅在此頁面需要的樣式 */
.short-input {
  width: 100px !important;
  margin-right: 10px;
}

.field-hint {
  font-size: 0.85em;
  color: #666;
  margin-left: 5px;
}

/* LINE帳號設置相關樣式 */
.line-setup-container {
  width: 100%;
  padding: 15px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.line-note {
  color: #666;
  font-size: 0.9em;
  margin-bottom: 15px;
  line-height: 1.6;
}

.line-accounts-summary {
  margin-top: 15px;
}

.line-summary-section {
  margin-bottom: 15px;
}

.line-summary-section h4 {
  margin: 0 0 10px 0;
  font-size: 1em;
  color: #333;
}

.line-account-list {
  list-style-type: none;
  padding-left: 10px;
  margin: 0;
}

.line-account-list li {
  padding: 5px 0;
  border-bottom: 1px solid #eee;
  font-size: 0.9em;
}

.line-account-list li:last-child {
  border-bottom: none;
}

/* 產品選擇區域樣式 */
.product-selection-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 15px;
  background-color: #f9f9f9;
  width: 100%; /* 確保容器與其他輸入框相同寬度 */
  box-sizing: border-box; /* 確保padding不會導致寬度溢出 */
  overflow-x: hidden; /* 避免出現水平滾動條 */
}

.product-search {
  margin-bottom: 15px;
  width: 98%; /* 稍微縮小搜索框寬度，避免水平滾動 */
  margin-left: auto;
  margin-right: auto;
}

.product-search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 固定每行顯示4個產品 */
  gap: 10px;
  width: 98%; /* 稍微縮小網格寬度 */
  margin-left: auto;
  margin-right: auto;
}

.product-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s;
  min-width: 0; /* 防止項目過大 */
}

.product-checkbox:hover {
  background-color: #eee;
}

.product-checkbox input[type="checkbox"] {
  flex-shrink: 0; /* 防止複選框被壓縮 */
  margin-right: 8px; /* 確保複選框和文字之間有間距 */
}

.product-checkbox .checkmark {
  flex-shrink: 0; /* 防止勾選框被壓縮 */
  min-width: 18px; /* 固定勾選框寬度 */
}

.product-name {
  margin-left: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: calc(100% - 30px); /* 為複選框預留足夠空間 */
  display: inline-block; /* 確保寬度正確套用 */
  cursor: help; /* 修改為help游標，提示用戶有提示信息 */
  position: relative; /* 為自定義提示定位 */
  border-bottom: 1px dotted #999; /* 添加虛線底邊，提示有提示信息 */
  color: #333; /* 設置文字顏色 */
  transition: color 0.2s; /* 添加過渡效果 */
}

/* 確保title提示能正常顯示 */
.product-checkbox:hover .product-name {
  color: #4CAF50; /* 在管理者模式下使用綠色 */
}

/* 確保選中狀態下的項目樣式 */
.product-checkbox input[type="checkbox"]:checked + .checkmark + .product-name {
  font-weight: bold;
  color: #4CAF50;
}

/* 移除舊的重複樣式 */
.product-checkbox span:last-child {
  margin-left: 0; /* 已由 .product-name 設定 */
}

@media (max-width: 1200px) {
  .checkbox-grid {
    grid-template-columns: repeat(3, 1fr); /* 在較小螢幕上每行顯示3個 */
  }
}

@media (max-width: 768px) {
  .checkbox-grid {
    grid-template-columns: repeat(1, 1fr); /* 在移動裝置上每行顯示1個 */
  }
  
  .product-selection-container {
    max-width: 100%; /* 確保在移動端與其他輸入框相同寬度 */
    margin: 0;
    padding: 10px;
  }
  
  .product-search,
  .checkbox-grid {
    width: 100%; /* 在移動端使用全寬 */
  }
  
  .form-group {
    max-width: 100%;
    box-sizing: border-box;
  }
  
  .form-group input,
  .form-group textarea,
  .product-selection-container {
    max-width: 100%;
    box-sizing: border-box;
  }
}
</style>
