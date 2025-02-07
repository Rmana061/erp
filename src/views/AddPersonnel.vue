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
              <label>員工工號：</label>
              <input type="text" v-model="personnelStaffNo" placeholder="（管理員自填）">
            </div>
            <div class="form-group">
              <label>人員權限：</label>
              <select v-model="personnelPermission">
                <option disabled value="">（選擇）</option>
                <option>最高權限</option>
                <option>普通權限</option>
                <option>基本權限</option>
                <option>檢視權限</option>
              </select>
            </div>

            <div class="button-group">
              <button class="submit-btn" @click="updatePersonnel">確認</button>
              <button class="cancel-btn" @click="navigateTo('Admin')">取消</button>
            </div>
          </div>

          <div class="permission-info">
            <h3>權限說明如下：</h3>
            <ul>
              <li>最高權限：可以檢視訂單、新增客戶、新增產品、新增操作人員、查看所有管理員操作紀錄</li>
              <li>普通權限：可以檢視訂單、新增客戶、新增產品</li>
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
  methods: {
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
    async fetchAdminDetails() {
      if (!this.$route.query.id) return;
      
      this.isEditMode = true;
      this.editId = this.$route.query.id;
      
      try {
        const response = await axios.post(getApiUrl(API_PATHS.ADMIN_DETAIL(this.editId)), {}, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          const admin = response.data.data;
          this.personnelAccount = admin.admin_account;
          this.personnelName = admin.admin_name;
          this.personnelStaffNo = admin.staff_no;
          this.personnelPermission = this.getPermissionName(admin.permission_level_id);
        } else {
          throw new Error(response.data.message || '獲取管理員資料失敗');
        }
      } catch (error) {
        console.error('Error fetching admin details:', error);
        alert('獲取管理員資料失敗：' + (error.response?.data?.message || error.message));
      }
    },
    getPermissionName(level_id) {
      const permissions = {
        1: '最高權限',
        2: '普通權限',
        3: '基本權限',
        4: '檢視權限'
      };
      return permissions[level_id] || '未知權限';
    },
    getPermissionId(permissionName) {
      const permissions = {
        '最高權限': 1,
        '普通權限': 2,
        '基本權限': 3,
        '檢視權限': 4
      };
      return permissions[permissionName] || 2;
    },
    async updatePersonnel() {
      if (!this.personnelAccount || !this.personnelName || !this.personnelStaffNo || !this.personnelPermission) {
        alert('請填寫所有必要欄位');
        return;
      }

      try {
        let response;
        const requestData = {
          admin_account: this.personnelAccount,
          admin_name: this.personnelName,
          staff_no: this.personnelStaffNo,
          permission_level_id: this.getPermissionId(this.personnelPermission)
        };

        if (this.personnelPassword) {
          requestData.admin_password = this.personnelPassword;
        }

        if (this.isEditMode) {
          // 編輯模式
          requestData.id = this.editId;
          response = await axios.post(getApiUrl(API_PATHS.ADMIN_UPDATE), requestData, {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          });
        } else {
          // 新增模式
          requestData.status = 'active';
          response = await axios.post(getApiUrl(API_PATHS.ADMIN_ADD), requestData, {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          });
        }

        if (response.data.status === 'success') {
          alert(this.isEditMode ? '人員更新成功！' : '人員新增成功！');
          this.$router.push('/admin');
        } else {
          throw new Error(response.data.message || (this.isEditMode ? '更新失敗' : '新增失敗'));
        }
      } catch (error) {
        console.error('Error updating/adding personnel:', error);
        alert((this.isEditMode ? '更新' : '新增') + '失敗：' + (error.response?.data?.message || error.message));
      }
    }
  },
  mounted() {
    document.title = '管理者系統';
    this.fetchAdminDetails();
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
