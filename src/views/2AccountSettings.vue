<!-- 帳號設定 -->
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
                <input v-if="isEditing" 
                  type="tel" 
                  v-model="editedInfo.phone"
                  @input="validatePhone" />
                <span v-else class="field-value">{{ customerInfo.phone || '未設置' }}</span>
              </div>
            </div>
            
            <div class="form-group">
              <label>Email：</label>
              <div class="input-container">
                <input v-if="isEditing" 
                  type="text" 
                  v-model="editedInfo.email"
                  @input="validateEmail" />
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
            <!-- LINE個人帳號部分 -->
            <div class="line-section">
              <button @click="showBindQRCode('user')" class="bind-button top-button">
                <span>綁定個人帳號</span>
              </button>
              <h4>個人帳號綁定</h4>
              <div class="line-content-container">
                <div v-if="lineUsers.length === 0" class="empty-status">
                  尚未綁定個人帳號
                </div>
                <div v-else class="line-accounts-list">
                  <div v-for="(user, index) in lineUsers" :key="'user-'+index" class="line-account-item">
                    <div class="account-info">
                      <span class="account-name">{{ user.user_name || '未知用戶' }}</span>
                    </div>
                    <button @click="unbindUser(user.id)" class="unbind-button mini">
                      解除綁定
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- LINE群組部分 -->
            <div class="line-section">
              <div class="group-instructions">
                <p>將LINE官方帳號加入您的群組後，在群組中發送「綁定帳號 您的帳號名稱」即可完成綁定。</p>
                <p>例如：綁定帳號 3333</p>
              </div>
              <h4>群組綁定</h4>
              <div class="line-content-container">
                <div v-if="lineGroups.length === 0" class="empty-status">
                  尚未綁定群組
                </div>
                <div v-else class="line-accounts-list">
                  <div v-for="(group, index) in lineGroups" :key="'group-'+index" class="line-account-item">
                    <div class="account-info">
                      <span class="account-name">{{ group.group_name || '未命名群組' }}</span>
                    </div>
                    <button @click="unbindGroup(group.id)" class="unbind-button mini">
                      解除綁定
                    </button>
                  </div>
                </div>
              </div>
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
import { logoutMixin } from '../mixins/logoutMixin';
import SideBar from '../components/SideBar.vue';
import axios from 'axios';
import { API_PATHS, getApiUrl } from '../config/api';
import QRCode from 'qrcode'

export default {
  name: 'AccountSettings',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin, logoutMixin],
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
      },
      lineUsers: [],
      lineGroups: [],
      currentBindType: 'user', // 'user' 或 'group'
      previousUserCount: 0 // 添加记录之前用户数量的变量
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
          
          // 獲取LINE用戶和群組資料
          this.lineUsers = response.data.data.line_users || [];
          this.lineGroups = response.data.data.line_groups || [];
          
          // 檢查是否剛剛完成綁定
          if (this.showQRModal) {
            // 檢查是否有新增的帳號或群組
            let bindSuccess = false;
            
            if (this.currentBindType === 'user' && this.lineUsers.length > this.previousUserCount) {
              bindSuccess = true;
            } else if (this.currentBindType === 'group' && this.lineGroups.length > 0) {
              bindSuccess = true;
            }
            
            if (bindSuccess) {
              this.closeQRModal();
              alert('LINE綁定成功！');
            }
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
    async showBindQRCode(type) {
      this.currentBindType = type;
      try {
        this.previousUserCount = this.lineUsers.length;
        
        const customerId = localStorage.getItem('customer_id');
        
        // 創建一個新的axios實例，避免共用cookie和session
        const tempAxios = axios.create({
          withCredentials: false  // 禁用credentials以避免傳送session cookie
        });
        
        const response = await tempAxios.post(getApiUrl(API_PATHS.GENERATE_BIND_URL), 
          {
            customer_id: customerId,
            bind_type: 'user'
          },
          {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          // 嘗試使用兩種可能的字段名
          const bindUrl = response.data.data.bind_url || response.data.data.url;
          
          if (!bindUrl) {
            throw new Error('回應中缺少綁定URL');
          }
          
          // 生成QR Code
          this.qrCodeUrl = await QRCode.toDataURL(bindUrl, {
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
    async unbindUser(userId) {
      if (!confirm('確定要解除LINE帳號綁定嗎？')) return;

      try {
        const customerId = localStorage.getItem('customer_id');
        // 存儲操作前的LINE用戶列表，用於後端比較變更
        const previousLineUsers = [...this.lineUsers];
        
        const response = await axios.post(getApiUrl(API_PATHS.UNBIND_LINE_USER), 
          { 
            customer_id: customerId, 
            user_id: userId,
            user_type: 'customer', // 指明操作者類型為客戶
            action_type: 'unbind_line_user', // 指明操作類型
            // 傳遞操作前的用戶資訊，幫助日誌記錄更詳細
            line_user_info: this.lineUsers.find(user => user.id === userId)
          },
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
        console.error('Error unbinding LINE user:', error);
        alert('解除LINE帳號綁定失敗：' + (error.response?.data?.message || error.message));
      }
    },
    async unbindGroup(groupId) {
      if (!confirm('確定要解除LINE群組綁定嗎？')) return;

      try {
        const customerId = localStorage.getItem('customer_id');
        // 存儲操作前的LINE群組列表，用於後端比較變更
        const previousLineGroups = [...this.lineGroups];
        
        const response = await axios.post(getApiUrl(API_PATHS.UNBIND_LINE_GROUP), 
          { 
            customer_id: customerId, 
            group_id: groupId,
            user_type: 'customer', // 指明操作者類型為客戶
            action_type: 'unbind_line_group', // 指明操作類型
            // 傳遞操作前的群組資訊，幫助日誌記錄更詳細
            line_group_info: this.lineGroups.find(group => group.id === groupId)
          },
          {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          alert('LINE群組解除綁定成功');
          await this.fetchCustomerInfo();  // 重新獲取客戶資料
        } else {
          throw new Error(response.data.message || '解除LINE群組綁定失敗');
        }
      } catch (error) {
        console.error('Error unbinding LINE group:', error);
        alert('解除LINE群組綁定失敗：' + (error.response?.data?.message || error.message));
      }
    },
    validatePhone(event) {
      // 只允許數字和特殊符號 (+、-、()、空格)
      const value = event.target.value;
      const filteredValue = value.replace(/[^0-9+\-() ]/g, '');
      if (value !== filteredValue) {
        this.editedInfo.phone = filteredValue;
      }
    },
    validateEmail(event) {
      // 只允許英文、數字和特定符號 (@、.、_、-、+)
      const value = event.target.value;
      const filteredValue = value.replace(/[^a-zA-Z0-9@._\-+]/g, '');
      if (value !== filteredValue) {
        this.editedInfo.email = filteredValue;
      }
    },
    handleEmailPaste(event) {
      // 阻止預設貼上行為
      event.preventDefault();
      
      // 獲取剪貼簿的文本
      const pastedText = event.clipboardData.getData('text');
      
      // 過濾不允許的字符
      const filteredText = pastedText
        .replace(/[^\x00-\x7F]/g, '')
        .replace(/[^a-zA-Z0-9@._\-+]/g, '');
      
      // 將過濾後的文本插入到當前位置
      this.editedInfo.email = filteredText;
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
    document.title = '合揚訂單系統';
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 整體頁面佈局 */
html, body {
  overflow-y: auto;
  height: 100%;
}

body.customer-mode {
  overflow-y: auto !important;
  -webkit-overflow-scrolling: touch;
  height: 100%;
  position: relative;
}

.container {
  min-height: 100vh;
  position: relative;
  overflow-y: auto;
  display: flex;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  height: 100vh;
  position: relative;
}

.content-wrapper {
  padding: 20px;
  overflow-y: auto;
  height: auto;
}

.top-button {
  display: block;
  margin-bottom: 12px;
  background-color: #06C755;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  text-align: center;
  width: 100%;
  transition: all 0.2s;
}

.top-button:hover {
  background-color: #05a648;
  transform: translateY(-2px);
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
  gap: 20px;
  flex-wrap: wrap;
}

.line-section {
  flex: 1;
  min-width: 250px;
  margin-bottom: 20px;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: 200px;
}

.line-content-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.line-section h4 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 1.1rem;
  color: #444;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 6px;
}

.empty-status {
  color: #888;
  font-style: italic;
  padding: 10px 0;
  flex-grow: 1;
  display: flex;
  align-items: center;
}

.line-accounts-list {
  margin-bottom: 10px;
  overflow-y: auto;
  max-height: 300px;
  -webkit-overflow-scrolling: touch;
}

.line-account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.account-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.account-name {
  font-weight: 600;
  display: block;
  color: #333;
}

.unbind-button.mini {
  padding: 5px 10px;
  font-size: 0.85rem;
  background-color: #f5f5f5;
  color: #f44336;
  border: 1px solid #f44336;
}

.unbind-button.mini:hover {
  background-color: #ffebee;
}

.line-buttons {
  display: none;
}

.bind-button.section-button {
  background-color: #06C755;
  color: white;
  padding: 6px 12px;
  font-size: 0.85rem;
  max-width: 150px;
  height: auto;
}

.bind-button.section-button:hover:not(:disabled) {
  background-color: #05a648;
  transform: translateY(-2px);
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
  body, html {
    overflow-y: auto !important;
    -webkit-overflow-scrolling: touch;
    height: auto !important;
  }

  body.customer-mode {
    overflow-y: auto !important;
    height: auto !important;
  }

  .container {
    overflow-y: auto !important;
    height: auto !important;
    min-height: 100vh;
  }

  .main-content {
    overflow-y: auto !important;
    height: auto !important;
  }

  .content-wrapper {
    overflow-y: auto !important;
    -webkit-overflow-scrolling: touch;
  }

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
    align-items: stretch;
    overflow-y: visible;
  }
  
  .line-section {
    width: 100%;
    min-height: auto;
    padding-bottom: 15px;
  }
  
  .line-content-container {
    min-height: 80px;
    max-height: none;
    overflow-y: visible;
  }
  
  .line-accounts-list {
    max-height: none;
    overflow-y: visible;
  }
  
  .top-button {
    margin-bottom: 15px;
    padding: 10px;
    font-size: 1rem;
  }
  
  .group-instructions {
    padding: 12px;
    margin-bottom: 15px;
    font-size: 1rem;
  }
  
  .page-title-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}

.group-instructions {
  background-color: #eaf7ff;
  border-left: 3px solid #1e88e5;
  padding: 10px 12px;
  margin-bottom: 15px;
  border-radius: 4px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.group-instructions p {
  margin: 5px 0;
}

.group-instructions p:last-child {
  font-weight: 500;
  color: #333;
}
</style>
