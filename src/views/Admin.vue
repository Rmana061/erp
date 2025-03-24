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
                <tr v-for="(admin, index) in paginatedAdmins" :key="admin.id">
                  <td>{{ admin.account }}</td>
                  <td>{{ admin.name }}</td>
                  <td>{{ admin.staff_no }}</td>
                  <td>{{ admin.permission_level }}</td>
                  <td>
                    <div class="table-button-group">
                      <button 
                        class="table-button edit" 
                        @click="editPersonnel(admin.id)"
                        v-permission="'can_add_personnel'"
                        v-if="canEdit(admin)">
                        編輯
                      </button>
                      <button 
                        class="table-button delete" 
                        @click="deletePersonnel(admin.id)"
                        v-permission="'can_add_personnel'"
                        v-if="canDelete(admin)">
                        刪除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination" v-if="totalPages > 1">
            <button 
              @click="previousPage" 
              :disabled="currentPage === 1">
              上一頁
            </button>
            <span>{{ currentPage }} / {{ totalPages }}</span>
            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages">
              下一頁
            </button>
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
      isSidebarActive: false,
      currentPage: 1,
      itemsPerPage: 20,
      currentAdminPermissionId: null
    };
  },
  computed: {
    // 計算總頁數
    totalPages() {
      return Math.ceil(this.admins.length / this.itemsPerPage);
    },
    // 計算當前頁顯示的管理員
    paginatedAdmins() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.admins.slice(start, end);
    }
  },
  methods: {
    // 判断是否可以编辑管理员的方法
    canEdit(admin) {
      // 获取当前管理员权限
      const adminInfoStr = sessionStorage.getItem('adminInfo');
      if (!adminInfoStr) return false;
      
      const adminInfo = JSON.parse(adminInfoStr);
      const currentPermissionId = parseInt(adminInfo.permission_level_id);
      
      // 获取当前管理员ID
      const currentAdminId = localStorage.getItem('admin_id');
      
      // 如果是自己的账号，允许编辑
      if (admin.id.toString() === currentAdminId) {
        return true; // 自己可以编辑自己
      }
      
      // 获取目标管理员的权限ID
      let targetPermissionId;
      switch(admin.permission_level) {
        case '最高權限': targetPermissionId = 1; break;
        case '審核權限': targetPermissionId = 2; break;
        case '基本權限': targetPermissionId = 3; break;
        case '檢視權限': targetPermissionId = 4; break;
        default: targetPermissionId = 0;
      }
      
      // 权限规则：
      // 1. 最高權限(1)可以编辑任何人
      // 2. 審核權限(2)只能编辑基本權限(3)和檢視權限(4)
      // 3. 基本權限(3)和檢視權限(4)不能编辑任何人
      
      if (currentPermissionId === 1) {
        // 最高权限可以编辑任何人
        return true;
      } else if (currentPermissionId === 2) {
        // 审核权限只能编辑基本权限和检视权限
        return targetPermissionId > 2;
      } else {
        // 基本权限和检视权限不能编辑任何人
        return false;
      }
    },
    
    // 判断是否可以删除管理员的方法
    canDelete(admin) {
      // 获取当前管理员权限
      const adminInfoStr = sessionStorage.getItem('adminInfo');
      if (!adminInfoStr) return false;
      
      const adminInfo = JSON.parse(adminInfoStr);
      const currentPermissionId = parseInt(adminInfo.permission_level_id);
      
      // 获取当前管理员ID
      const currentAdminId = localStorage.getItem('admin_id');
      
      // 如果是自己的账号，不允许删除
      if (admin.id.toString() === currentAdminId) {
        return false; // 不能删除自己
      }
      
      // 获取目标管理员的权限ID
      let targetPermissionId;
      switch(admin.permission_level) {
        case '最高權限': targetPermissionId = 1; break;
        case '審核權限': targetPermissionId = 2; break;
        case '基本權限': targetPermissionId = 3; break;
        case '檢視權限': targetPermissionId = 4; break;
        default: targetPermissionId = 0;
      }
      
      // 权限规则同编辑
      if (currentPermissionId === 1) {
        // 最高权限可以删除任何人(除了自己)
        return true;
      } else if (currentPermissionId === 2) {
        // 审核权限只能删除基本权限和检视权限
        return targetPermissionId > 2;
      } else {
        // 基本权限和检视权限不能删除任何人
        return false;
      }
    },
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    },
    closeSidebar() {
      this.isSidebarActive = false;
    },
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
    
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },
 
    async deletePersonnel(adminId) {
      // 检查是否可以删除此管理员
      const adminToDelete = this.admins.find(a => a.id === adminId);
      if (!adminToDelete) return;
      
      // 检查删除权限
      if (!this.canDelete(adminToDelete)) {
        const currentAdminId = localStorage.getItem('admin_id');
        if (adminId.toString() === currentAdminId) {
          alert('無法刪除自己的帳號');
        } else {
          alert('您無權刪除該管理員');
        }
        return;
      }
      
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
      // 检查是否可以编辑此管理员
      const adminToEdit = this.admins.find(a => a.id === adminId);
      if (!adminToEdit) return;
      
      if (!this.canEdit(adminToEdit)) {
        alert('您無權編輯該管理員');
        return;
      }
      
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
    document.title = '合揚訂單後台系統';
    this.fetchAdmins();
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';
</style>
