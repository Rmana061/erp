<!-- 新增人員 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,<button class="logout-button" @click="logout">登出</button></span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
          <div class="page-header">
            <h2>管理員（新增人員）</h2>
          </div>

          <div class="form-container">
            <div class="form-group">
              <label>人員帳號：</label>
              <input type="text" v-model="personnelAccount" placeholder="（管理員自填）">
            </div>
            <div class="form-group">
              <label>人員密碼：</label>
              <input type="password" v-model="personnelPassword" placeholder="（管理員自填）">
            </div>
            <div class="form-group">
              <label>人員姓名：</label>
              <input type="text" v-model="personnelName" placeholder="（管理員自填）">
            </div>
            <div class="form-group">
              <label>人員工號：</label>
              <input type="text" v-model="personnelStaffNo" placeholder="（管理員自填）">
            </div>
            <div class="form-group">
              <label>人員權限：</label>
              <select v-model="personnelPermission">
                <option disabled value="">（選擇）</option>
                <option v-for="permission in availablePermissions" :key="permission.id" :value="permission.name">
                  {{ permission.name }}
                </option>
              </select>
            </div>

            <div class="button-group">
              <button class="submit-btn" @click="submitPersonnel">確認</button>
              <button class="cancel-btn" @click="navigateTo('Admin')">取消</button>
            </div>
          </div>

          <div class="permission-info">
            <h3>權限說明如下：</h3>
            <div class="permission-table">
              <div class="permission-row">
                <div class="permission-type">最高權限：</div>
                <div class="permission-desc">可以審核訂單、新增客戶、新增產品、新增操作人員、查看所有管理員操作紀錄</div>
              </div>
              <div class="permission-row">
                <div class="permission-type">審核權限：</div>
                <div class="permission-desc">可以審核訂單、新增客戶、新增產品、新增操作人員</div>
              </div>
              <div class="permission-row">
                <div class="permission-type">基本權限：</div>
                <div class="permission-desc">可以新增客戶、新增產品</div>
              </div>
              <div class="permission-row">
                <div class="permission-type">檢視權限：</div>
                <div class="permission-desc">僅供檢視</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import axios from 'axios';
import SideBar from '../components/SideBar.vue';
import { adminMixin } from '../mixins/adminMixin';
import { timeMixin } from '../mixins/timeMixin';
import { logoutMixin } from '../mixins/logoutMixin';
import { API_PATHS, getApiUrl } from '../config/api';
import axiosInstance from '../config/axios';

export default {
  name: 'AddPersonnel',
  mixins: [adminMixin, timeMixin, logoutMixin],
  components: {
    SideBar
  },
  data() {
    return {
      personnelAccount: '',
      personnelPassword: '',
      personnelName: '',
      personnelStaffNo: '',
      personnelPermission: '',
      isEditMode: false,
      editId: null,
      currentAdminPermissionId: 1 // 默認為最高權限，將在created中更新
    };
  },
  computed: {
    // 根據當前管理員權限過濾可用的權限選項
    availablePermissions() {
      const allPermissions = [
        { id: 1, name: '最高權限' },
        { id: 2, name: '審核權限' },
        { id: 3, name: '基本權限' },
        { id: 4, name: '檢視權限' }
      ];
      
      // 只返回當前管理員權限級別及以下的權限
      return allPermissions.filter(permission => permission.id >= this.currentAdminPermissionId);
    }
  },
  async created() {
    await this.getCurrentAdminPermission();
    await this.fetchAdminDetails();
  },
  methods: {
    // 獲取當前登錄管理員的權限級別
    async getCurrentAdminPermission() {
      try {
        const adminId = localStorage.getItem('admin_id');
        if (!adminId) {
          this.$router.push('/admin-login');
          return;
        }
        
        const adminInfoStr = sessionStorage.getItem('adminInfo');
        if (adminInfoStr) {
          const adminInfo = JSON.parse(adminInfoStr);
          this.currentAdminPermissionId = adminInfo.permission_level_id;
        } else {
          // 如果無法從sessionStorage獲取，則嘗試從API獲取
          const response = await axiosInstance.post(API_PATHS.ADMIN_INFO, {
            admin_id: adminId
          });
          
          if (response.data.status === 'success') {
            this.currentAdminPermissionId = response.data.data.permission_level_id;
          }
        }
      } catch (error) {
        console.error('Error getting current admin permission:', error);
      }
    },
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
    async fetchAdminDetails() {
      if (!this.$route.query.id) return;
      
      this.isEditMode = true;
      this.editId = this.$route.query.id;
      
      try {
        const adminId = localStorage.getItem('admin_id');
        if (!adminId) {
          this.$router.push('/admin-login');
          return;
        }

        const response = await axiosInstance.post(API_PATHS.ADMIN_INFO, {
          admin_id: this.editId
        });

        if (response.data.status === 'success') {
          const admin = response.data.data;
          this.personnelAccount = admin.admin_account;
          this.personnelName = admin.admin_name;
          this.personnelStaffNo = admin.staff_no || '';
          this.personnelPermission = this.getPermissionName(admin.permission_level_id);
        } else {
          throw new Error(response.data.message || '获取管理员资料失败');
        }
      } catch (error) {
        console.error('Error fetching admin details:', error);
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_id');
          sessionStorage.removeItem('adminInfo');
          this.$router.push('/admin-login');
          return;
        }
        alert('获取管理员资料失败：' + (error.response?.data?.message || error.message));
      }
    },
    getPermissionName(level_id) {
      const permissions = {
        1: '最高權限',
        2: '審核權限',
        3: '基本權限',
        4: '檢視權限'
      };
      return permissions[level_id] || '未知權限';
    },
    getPermissionId(permissionName) {
      const permissions = {
        '最高權限': 1,
        '審核權限': 2,
        '基本權限': 3,
        '檢視權限': 4
      };
      return permissions[permissionName] || 2;
    },
    async submitPersonnel() {
      if (!this.validateForm()) return;

      try {
        // 获取认证信息
        const adminId = localStorage.getItem('admin_id');
        const adminInfo = sessionStorage.getItem('adminInfo');

        if (!adminId || !adminInfo) {
          console.log('未登录或会话已过期');
          localStorage.removeItem('admin_id');
          sessionStorage.removeItem('adminInfo');
          sessionStorage.removeItem('isAuthenticated');
          this.$router.push('/admin-login');
          return;
        }

        // 准备提交数据
        const personnelData = {
          admin_account: this.personnelAccount,
          admin_name: this.personnelName,
          staff_no: this.personnelStaffNo,
          permission_level_id: this.getPermissionId(this.personnelPermission),
          current_admin_id: adminId  // 添加当前管理员ID
        };

        // 如果是新增或有修改密码，则添加密码字段
        if (!this.isEditMode || this.personnelPassword) {
          personnelData.admin_password = this.personnelPassword;
        }

        // 如果是编辑模式，添加ID
        if (this.isEditMode) {
          personnelData.id = this.editId;
        }

        // 发送请求
        const response = await axiosInstance.post(
          this.isEditMode ? API_PATHS.ADMIN_UPDATE : API_PATHS.ADMIN_ADD,
          personnelData,
          {
            headers: {
              'Authorization': `Bearer ${adminId}`
            }
          }
        );

        if (response.data.status === 'success') {
          alert(this.isEditMode ? '管理員更新成功！' : '管理員新增成功！');
          await this.$router.push({ name: 'Admin' });
        } else {
          throw new Error(response.data.message || '操作失敗');
        }
      } catch (error) {
        console.error('Error submitting personnel:', error);
        
        if (error.response?.status === 401) {
          console.log('Session expired or unauthorized');
          localStorage.removeItem('admin_id');
          sessionStorage.removeItem('adminInfo');
          sessionStorage.removeItem('isAuthenticated');
          this.$router.push('/admin-login');
          return;
        }
        
        alert('操作失敗：' + (error.response?.data?.message || error.message));
      }
    },
    validateForm() {
      const requiredFields = ['personnelAccount', 'personnelName', 'personnelStaffNo', 'personnelPermission'];
      
      if (!this.isEditMode && !this.personnelPassword) {
        alert('請填寫密碼');
        return false;
      }
      
      for (const field of requiredFields) {
        if (!this[field]) {
          alert('請填寫所有必要欄位');
          return false;
        }
      }

      // 檢查權限是否合法（防止手動修改DOM繞過權限限制）
      const permissionId = this.getPermissionId(this.personnelPermission);
      if (permissionId < this.currentAdminPermissionId) {
        alert('您無權新增比自己權限更高的管理員');
        return false;
      }
      
      return true;
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */

.permission-info {
  max-width: 800px;
  margin: 40px auto;
  text-align: center;
}

.permission-info h3 {
  margin-bottom: 20px;
}

.permission-table {
  display: inline-block;
  text-align: left;
  margin: 0 auto;
}

.permission-row {
  display: flex;
  margin-bottom: 10px;
}

.permission-type {
  width: 100px;
  text-align: right;
  padding-right: 10px;
}

.permission-desc {
  flex: 1;
  text-align: left;
}
</style>
