<!-- 帳號設定 -->
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
        <div class="page-header">
          <h2>帳號設定</h2>
        </div>

        <div class="account-info">
          <div class="info-grid">
            <p><strong>公司名稱：</strong></p>
            <p>{{ customerInfo.company_name || '載入中...' }}</p>
            <p><strong>帳號：</strong></p>
            <p>{{ customerInfo.username || '載入中...' }}</p>
            <p><strong>密碼：</strong></p>
            <p>********</p>
          </div>
          <div class="line-settings">
            <p><strong>LINE帳號綁定</strong></p>
            <div class="line-buttons">
              <button @click="bindAccount" :disabled="customerInfo.line_account">綁定帳號</button>
              <button @click="unbindAccount" :disabled="!customerInfo.line_account">解除綁定</button>
            </div>
            <p v-if="customerInfo.line_account" class="line-status">
              已綁定：{{ customerInfo.line_account }}
            </p>
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
  name: 'AccountSettings',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  data() {
    return {
      customerInfo: {}
    };
  },
  methods: {
    async fetchCustomerInfo() {
      try {
        // 首先检查是否有customer_id
        const customerId = localStorage.getItem('customer_id');
        if (!customerId) {
          this.$router.push('/customer-login');
          return;
        }

        const response = await axios.post(getApiUrl(API_PATHS.CUSTOMER_INFO), 
          { customer_id: customerId },  // 添加 customer_id 到请求体
          {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          this.customerInfo = response.data.data;
        } else {
          throw new Error(response.data.message || '獲取客戶資料失敗');
        }
      } catch (error) {
        console.error('Error fetching customer info:', error);
        if (error.response?.status === 401) {
          this.$router.push('/customer-login');
        } else {
          alert('獲取客戶資料失敗：' + (error.response?.data?.message || error.message));
        }
      }
    },
    async bindAccount() {
      try {
        const response = await axios.post(getApiUrl(API_PATHS.BIND_LINE), {}, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          window.location.href = response.data.data.url;
        } else {
          throw new Error(response.data.message || 'LINE帳號綁定失敗');
        }
      } catch (error) {
        console.error('Error binding LINE account:', error);
        alert('LINE帳號綁定失敗：' + (error.response?.data?.message || error.message));
      }
    },
    async unbindAccount() {
      if (!confirm('確定要解除LINE帳號綁定嗎？')) return;

      try {
        const customerId = localStorage.getItem('customer_id');
        const response = await axios.post(getApiUrl(API_PATHS.UNBIND_LINE), 
          { customer_id: customerId },  // 添加 customer_id 到请求体
          {
            withCredentials: true
          }
        );

        if (response.data.status === 'success') {
          alert('LINE帳號解除綁定成功');
          this.fetchCustomerInfo();
        } else {
          throw new Error(response.data.message || '解除LINE帳號綁定失敗');
        }
      } catch (error) {
        console.error('Error unbinding LINE account:', error);
        alert('解除LINE帳號綁定失敗：' + (error.response?.data?.message || error.message));
      }
    }
  },
  created() {
    this.fetchCustomerInfo();
  },
  mounted() {
    document.title = '客戶系統';
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

.line-status {
  margin-top: 10px;
  color: #4CAF50;
  font-size: 0.9em;
}

/* 所有其他樣式已移至 unified-base */
</style>
