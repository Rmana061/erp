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
        <div class="page-title-container">
          <h2 class="page-title">帳號設定</h2>
          
          <!-- 编辑模式切换按钮 -->
          <div class="edit-toggle">
            <button @click="toggleEditMode" class="edit-button">
              {{ isEditing ? '取消編輯' : '編輯資料' }}
            </button>
            <button v-if="isEditing" @click="saveChanges" class="save-button">
              保存變更
            </button>
          </div>
        </div>

        <!-- 顯示和編輯客戶資料表格 -->
        <div class="card account-detail-form">
          <h3 class="card-title">基本資料</h3>
          <div class="form-row">
            <div class="form-group">
              <label>公司名稱：</label>
              <div class="input-container">
                <input v-if="isEditing" type="text" v-model="editedInfo.company_name" />
                <span v-else class="field-value">{{ customerInfo.company_name || '載入中...' }}</span>
              </div>
            </div>
            
            <div class="form-group">
              <label>帳號：</label>
              <div class="input-container">
                <span class="field-value">{{ customerInfo.username || '載入中...' }}</span>
                <small class="field-note">(帳號不可修改)</small>
              </div>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>密碼：</label>
              <div class="input-container">
                <input v-if="isEditing" type="password" v-model="editedInfo.password" placeholder="輸入新密碼，留空表示不變更" />
                <span v-else class="field-value">********</span>
              </div>
            </div>
            
            <div class="form-group">
              <label>聯絡人：</label>
              <div class="input-container">
                <input v-if="isEditing" type="text" v-model="editedInfo.contact_name" />
                <span v-else class="field-value">{{ customerInfo.contact_person || customerInfo.contact_name || '未設置' }}</span>
              </div>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>電話：</label>
              <div class="input-container">
                <input v-if="isEditing" type="tel" v-model="editedInfo.phone" />
                <span v-else class="field-value">{{ customerInfo.phone || '未設置' }}</span>
              </div>
            </div>
            
            <div class="form-group">
              <label>Email：</label>
              <div class="input-container">
                <input v-if="isEditing" type="email" v-model="editedInfo.email" />
                <span v-else class="field-value">{{ customerInfo.email || '未設置' }}</span>
              </div>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full-width">
              <label>地址：</label>
              <div class="input-container">
                <input v-if="isEditing" type="text" v-model="editedInfo.address" />
                <span v-else class="field-value">{{ customerInfo.address || '未設置' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- LINE 帳號綁定區域 -->
        <div class="card line-settings-section">
          <h3 class="card-title">LINE帳號綁定</h3>
          <div class="line-settings">
            <div class="line-status-display">
              <div class="status-row">
                <span class="status-label">LINE帳號狀態：</span>
                <span class="status-value" :class="{'line-bound': customerInfo.line_account}">
                  {{ customerInfo.line_account ? '已綁定' : '未綁定' }}
                </span>
              </div>
              <div v-if="customerInfo.line_account" class="status-row">
                <span class="status-label">已綁定帳號：</span>
                <span class="line-account-id">{{ customerInfo.line_account }}</span>
              </div>
            </div>
            <div class="line-buttons">
              <button @click="showBindQRCode" :disabled="!!customerInfo.line_account" class="bind-button">
                <span>綁定帳號</span>
              </button>
              <button @click="unbindAccount" :disabled="!customerInfo.line_account" class="unbind-button">
                <span>解除綁定</span>
              </button>
            </div>
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
      checkBindingInterval: null,
      isEditing: false,
      editedInfo: {
        company_name: '',
        password: '',
        contact_name: '',
        phone: '',
        email: '',
        address: ''
      }
    };
  },
  methods: {
    toggleEditMode() {
      if (this.isEditing) {
        // 取消編輯，恢復原始資料
        this.isEditing = false;
      } else {
        // 進入編輯模式，初始化編輯資料
        this.editedInfo = {
          company_name: this.customerInfo.company_name || '',
          password: '',  // 密碼欄位留空
          contact_name: this.customerInfo.contact_person || this.customerInfo.contact_name || '',
          phone: this.customerInfo.phone || '',
          email: this.customerInfo.email || '',
          address: this.customerInfo.address || ''
        };
        this.isEditing = true;
      }
    },
    async saveChanges() {
      try {
        // 移除空密碼字段，表示不需更新密碼
        const updateData = { ...this.editedInfo };
        if (!updateData.password) {
          delete updateData.password;
        }
        
        // 添加客戶ID
        const customerId = localStorage.getItem('customer_id');
        updateData.customer_id = customerId;

        const response = await axios.post(getApiUrl(API_PATHS.UPDATE_CUSTOMER_INFO), 
          updateData,
          {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          alert('資料更新成功！');
          this.isEditing = false;
          await this.fetchCustomerInfo();  // 重新獲取更新後的資料
        } else {
          throw new Error(response.data.message || '更新資料失敗');
        }
      } catch (error) {
        console.error('Error updating customer info:', error);
        alert('更新資料失敗：' + (error.response?.data?.message || error.message));
      }
    },
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

/* 整體頁面佈局 */
.content-wrapper {
  padding: 20px;
}

.page-title-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.page-title {
  margin: 0;
  color: #333;
  font-size: 1.8rem;
}

/* 卡片樣式 */
.card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  padding: 25px;
  margin-bottom: 30px;
}

.card-title {
  margin-top: 0;
  margin-bottom: 20px;
  color: #444;
  font-size: 1.3rem;
  font-weight: 600;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

/* 表單樣式 */
.form-row {
  display: flex;
  margin-bottom: 20px;
  gap: 30px;
}

.form-group {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: flex-start;
}

.form-group label {
  width: 80px;
  color: #666;
  font-weight: 500;
  text-align: right;
  padding-right: 10px;
  padding-top: 8px;
  flex-shrink: 0;
}

.input-container {
  flex: 1;
  min-width: 0;
}

.field-value {
  display: inline-block;
  padding: 8px 0;
  min-height: 20px;
  color: #333;
}

.field-note {
  display: block;
  margin-top: 4px;
  color: #888;
  font-size: 0.85rem;
}

.full-width {
  flex-basis: 100%;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #6366F1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* 編輯按鈕 */
.edit-toggle {
  display: flex;
  gap: 10px;
}

.edit-button, .save-button {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-button {
  background-color: #f0f0f0;
  color: #333;
}

.save-button {
  background-color: #4CAF50;
  color: white;
}

.edit-button:hover {
  background-color: #e0e0e0;
}

.save-button:hover {
  background-color: #3d8b40;
}

/* LINE綁定部分 */
.line-settings {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.line-status-display {
  flex: 1;
  min-width: 0;
}

.status-row {
  display: flex;
  margin-bottom: 10px;
  align-items: center;
}

.status-label {
  width: 120px;
  text-align: right;
  padding-right: 10px;
  color: #666;
  font-weight: 500;
  flex-shrink: 0;
}

.status-value {
  font-weight: 600;
}

.line-account-id {
  color: #4CAF50;
  word-break: break-all;
}

.line-bound {
  color: #4CAF50;
  font-weight: 600;
}

.line-buttons {
  display: flex;
  gap: 12px;
}

.line-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bind-button {
  background-color: #06C755;
  color: white;
}

.unbind-button {
  background-color: #f44336;
  color: white;
}

.bind-button:hover:not(:disabled) {
  background-color: #05a648;
  transform: translateY(-2px);
}

.unbind-button:hover:not(:disabled) {
  background-color: #e53935;
  transform: translateY(-2px);
}

.line-buttons button:disabled {
  background-color: #e0e0e0;
  color: #999;
  cursor: not-allowed;
  transform: none;
}

/* QR 模態視窗 */
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
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
  position: relative;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.close-button {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.close-button:hover {
  color: #333;
}

.qr-container {
  margin: 24px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  border: 1px solid #eee;
  padding: 10px;
  border-radius: 8px;
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
  font-size: 15px;
  line-height: 1.6;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 20px;
  }
  
  .form-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .form-group label {
    width: 100%;
    text-align: left;
    margin-bottom: 5px;
    padding-top: 0;
  }
  
  .line-settings {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }
  
  .status-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .status-label {
    width: 100%;
    text-align: left;
    margin-bottom: 5px;
  }
  
  .page-title-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>
