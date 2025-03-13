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
              <div class="checkbox-group">
                <label v-for="(product, index) in products" :key="index" class="custom-checkbox">
                  <input type="checkbox" v-model="newCustomer.selectedProducts" :value="product.value">
                  <span class="checkmark"></span>
                  <span>{{ product.name }}</span>
                </label>
              </div>
            </div>
            <div class="form-group">
              <label>LINE帳號綁定：</label>
              <input type="text" v-model="newCustomer.lineAccount" placeholder="">
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
      newCustomer: {
        companyName: '',
        account: '',
        password: '',
        selectedProducts: [],
        lineAccount: '',
        contactPerson: '',
        phone: '',
        email: '',
        address: '',
        reorderLimitDays: 2,
        notes: ''
      },
      products: [],
      editingId: null
    };
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
            lineAccount: customerData.line_account || '',
            contactPerson: customerData.contact_person || '',
            phone: customerData.phone || '',
            email: customerData.email || '',
            address: customerData.address || '',
            reorderLimitDays: customerData.reorder_limit_days || 2,
            notes: customerData.remark || ''
          };
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
          line_account: this.newCustomer.lineAccount,
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
          // 编辑现有客户
          customerData.id = this.editingId;
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
    document.title = '管理者系統';
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

/* 表单容器样式 */
.form-container {
  background-color: #f5fffa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.form-group {
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
}

.form-group label {
  width: 120px;
  text-align: right;
  margin-right: 10px;
  padding-top: 8px;
}

.form-group input,
.form-group textarea {
  width: calc(100% - 135px);
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  width: calc(100% - 135px);
  gap: 5px;
}

.checkbox-group .custom-checkbox {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 5px 0;
}

.checkbox-group .custom-checkbox input[type="checkbox"] {
  margin-right: 8px;
}

.checkbox-group .custom-checkbox .checkmark {
  margin-right: 8px;
}

.button-group {
  margin-top: 20px;
  text-align: center;
}

.button-group button {
  margin: 0 10px;
  padding: 8px 20px;
}

.short-input {
  width: 100px !important;
  margin-right: 10px;
}

.field-hint {
  font-size: 0.85em;
  color: #666;
  margin-left: 5px;
}
</style>
