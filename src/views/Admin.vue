<!-- 使用者 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <button class="bookmark-toggle" @click="toggleSidebar">
      <span class="bookmark-text">選單</span>
    </button>
    <div class="sidebar-overlay" :class="{ active: isSidebarActive }" @click="closeSidebar"></div>
    <SideBar menu-type="admin" :class="{ active: isSidebarActive }" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,<button class="logout-button" @click="logout">登出</button></span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
          <h2>管理員</h2>
          <div class="action-buttons">
            <button 
              class="action-button" 
              @click="navigateTo('AddPersonnel')"
              v-permission="'can_add_personnel'">
              + 新增人員
            </button>
            <button 
              class="action-button" 
              @click="navigateTo('LogRecords')"
              v-permission="'can_view_system_logs'">
              查詢操作紀錄
            </button>
          </div>

          <div class="table-container">
            <table class="admin-list">
              <thead>
                <tr>
                  <th>帳號</th>
                  <th>姓名</th>
                  <th>工號</th>
                  <th>權限等級</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(admin, index) in admins" :key="admin.id">
                  <td>{{ admin.account }}</td>
                  <td>{{ admin.name }}</td>
                  <td>{{ admin.staff_no }}</td>
                  <td>{{ admin.permission_level }}</td>
                  <td>
                    <div class="table-button-group">
                      <button 
                        class="table-button edit" 
                        @click="editPersonnel(admin.id)"
                        v-permission="'can_add_personnel'">
                        編輯
                      </button>
                      <button 
                        class="table-button delete" 
                        @click="deletePersonnel(admin.id)"
                        v-permission="'can_add_personnel'">
                        刪除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
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
  name: 'Admin',
  mixins: [adminMixin, timeMixin, logoutMixin],
  components: {
    SideBar
  },
  data() {
    return {
      admins: [],
      isSidebarActive: false
    };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    },
    closeSidebar() {
      this.isSidebarActive = false;
    },
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
 
    async deletePersonnel(adminId) {
      if (!confirm('確定要刪除此管理員嗎？')) return;

      try {
        const response = await axiosInstance.post(API_PATHS.ADMIN_DELETE, {
          id: adminId
        });

        if (response.data.status === 'success') {
          alert('管理員刪除成功');
          await this.fetchAdmins();
        } else {
          throw new Error(response.data.message || '刪除失敗');
        }
      } catch (error) {
        console.error('Error deleting admin:', error);
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_id');
          sessionStorage.removeItem('adminInfo');
          this.$router.push('/admin-login');
          return;
        }
        alert('刪除失敗：' + (error.response?.data?.message || error.message));
      }
    },
    editPersonnel(adminId) {
      // 檢查是否有管理員 ID 和權限
      const adminInfo = sessionStorage.getItem('adminInfo');
      if (!adminInfo || !localStorage.getItem('admin_id')) {
        alert('請重新登入');
        this.$router.push('/admin-login');
        return;
      }

      this.$router.push({
        name: 'AddPersonnel',
        query: { 
          id: adminId,
          mode: 'edit'
        }
      });
    },
    async fetchAdmins() {
      try {
        const response = await axiosInstance.post(API_PATHS.ADMIN_LIST, {
          type: 'admin'
        });
        
        if (response.data.status === 'success') {
          this.admins = response.data.data.map(admin => ({
            id: admin.id,
            account: admin.admin_account,
            name: admin.admin_name,
            staff_no: admin.staff_no || '-',
            permission_level: this.getPermissionName(admin.permission_level_id)
          }));
        } else {
          throw new Error(response.data.message || '獲取管理員列表失敗');
        }
      } catch (error) {
        console.error('Error fetching admins:', error);
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_id');
          sessionStorage.removeItem('adminInfo');
          this.$router.push('/admin-login');
          return;
        }
        alert('獲取管理員列表失敗：' + (error.response?.data?.message || error.message));
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
    }
  },
  mounted() {
    document.title = '管理者系統';
    this.fetchAdmins();
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';
</style>
