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
              <button @click="showBindQRCode" :disabled="!!customerInfo.line_account">綁定帳號</button>
              <button @click="unbindAccount" :disabled="!customerInfo.line_account">解除綁定</button>
            </div>
            <p v-if="customerInfo.line_account" class="line-status">
              已綁定：{{ customerInfo.line_account }}
            </p>
          </div>
        </div>

        <!-- QR Code Modal -->
        <div v-if="showQRModal" class="modal">
          <div class="modal-content">
            <span class="close-button" @click="closeQRModal">&times;</span>
            <h3>掃描QR Code綁定LINE帳號</h3>
            <div class="qr-container">
              <img :src="qrCodeUrl" alt="QR Code" v-if="qrCodeUrl">
              <div v-else class="loading">生成QR Code中...</div>
            </div>
            <p class="qr-instructions">
              請使用LINE掃描此QR Code來綁定您的帳號。<br>
              綁定後即可透過LINE接收訂單通知及查詢訂單狀態。
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
import QRCode from 'qrcode'

export default {
  name: 'AccountSettings',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  data() {
    return {
      customerInfo: {},
      showQRModal: false,
      qrCodeUrl: '',
      checkBindingInterval: null
    };
  },
  methods: {
    async fetchCustomerInfo() {
      try {
        const customerId = localStorage.getItem('customer_id');
        if (!customerId) {
          this.$router.push('/customer-login');
          return;
        }

        const response = await axios.post(getApiUrl(API_PATHS.CUSTOMER_INFO), 
          { customer_id: customerId },
          {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          this.customerInfo = response.data.data;
          // 如果檢測到 line_account 有變化，關閉 QR code 視窗
          if (this.customerInfo.line_account && this.showQRModal) {
            this.closeQRModal();
            // 顯示成功消息
            alert('LINE帳號綁定成功！');
          }
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
    async showBindQRCode() {
      try {
        const customerId = localStorage.getItem('customer_id');
        const response = await axios.post(getApiUrl(API_PATHS.GENERATE_BIND_URL), {
          customer_id: customerId
        });

        if (response.data.status === 'success') {
          // 生成 QR Code
          this.qrCodeUrl = await QRCode.toDataURL(response.data.data.url, {
            width: 300,
            margin: 2,
            color: {
              dark: '#000000',
              light: '#ffffff'
            }
          });
          this.showQRModal = true;
          
          // 開始定期檢查綁定狀態
          this.startBindingCheck();
        } else {
          throw new Error(response.data.message || '生成QR Code失敗');
        }
      } catch (err) {
        console.error('Error generating QR code:', err);
        alert('生成QR Code失敗：' + (err.response?.data?.message || err.message));
      }
    },
    startBindingCheck() {
      // 每3秒檢查一次綁定狀態
      this.checkBindingInterval = setInterval(() => {
        this.fetchCustomerInfo();
      }, 3000);
    },
    closeQRModal() {
      this.showQRModal = false;
      this.qrCodeUrl = '';
      // 清除定時檢查
      if (this.checkBindingInterval) {
        clearInterval(this.checkBindingInterval);
        this.checkBindingInterval = null;
      }
    },
    async unbindAccount() {
      if (!confirm('確定要解除LINE帳號綁定嗎？')) return;

      try {
        const customerId = localStorage.getItem('customer_id');
        const response = await axios.post(getApiUrl(API_PATHS.UNBIND_LINE), 
          { customer_id: customerId },
          {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          alert('LINE帳號解除綁定成功');
          await this.fetchCustomerInfo();  // 重新獲取客戶資料
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
  beforeDestroy() {
    // 組件銷毀前清除定時器
    if (this.checkBindingInterval) {
      clearInterval(this.checkBindingInterval);
    }
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

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
  position: relative;
  text-align: center;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.qr-container {
  margin: 20px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.qr-container img {
  max-width: 100%;
  height: auto;
}

.loading {
  color: #666;
  font-size: 16px;
}

.qr-instructions {
  margin-top: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* 所有其他樣式已移至 unified-base */
</style>
