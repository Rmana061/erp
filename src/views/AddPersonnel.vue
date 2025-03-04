<!-- 新增人員 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,</span>
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
                <option>最高權限</option>
                <option>審核權限</option>
                <option>基本權限</option>
                <option>檢視權限</option>
              </select>
            </div>

            <div class="button-group">
              <button class="submit-btn" @click="submitPersonnel">確認</button>
              <button class="cancel-btn" @click="navigateTo('Admin')">取消</button>
            </div>
          </div>

          <div class="permission-info">
            <h3>權限說明如下：</h3>
            <ul>
              <li>最高權限：可以檢視訂單、新增客戶、新增產品、新增操作人員、查看所有管理員操作紀錄</li>
              <li>審核權限：可以檢視訂單、新增客戶、新增產品</li>
              <li>基本權限：可以新增客戶、新增產品</li>
              <li>檢視權限：僅供檢視</li>
            </ul>
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
import { API_PATHS, getApiUrl } from '../config/api';
import axiosInstance from '../config/axios';

export default {
  name: 'AddPersonnel',
  mixins: [adminMixin, timeMixin],
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
      editId: null
    };
  },
  async created() {
    await this.fetchAdminDetails();
  },
  methods: {
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
      return true;
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
