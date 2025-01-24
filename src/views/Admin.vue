<!-- 使用者 -->
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
          <h2>管理員</h2>
          <div class="action-buttons">
            <button class="action-button" @click="navigateTo('AddPersonnel')">+ 新增人員</button>
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
                    <button class="edit-btn" @click="editPersonnel(admin.id)">編輯</button>
                    <button class="delete-btn" @click="deletePersonnel(admin.id)">刪除</button>
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
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'Admin',
  mixins: [adminMixin, timeMixin],
  components: {
    SideBar
  },
  data() {
    return {
      admins: []
    };
  },
  methods: {
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
    // deletePersonnel(adminId) {
    //   if (confirm('確定要刪除此人員嗎？')) {
    //     axios.delete(getApiUrl(API_PATHS.ADMIN_DELETE), {
    //       data: { id: adminId },
    //       withCredentials: true,
    //       headers: {
    //         'Content-Type': 'application/json'
    //       }
    //     })
    //     .then(response => {
    //       if (response.data.status === 'success') {
    //         this.fetchAdmins();
    //         alert('人員已成功刪除');
    //       } else {
    //         throw new Error(response.data.message || '刪除人員失敗');
    //       }
    //     })
    //     .catch(error => {
    //       console.error('Error deleting admin:', error);
    //       alert('刪除人員時發生錯誤：' + (error.response?.data?.message || error.message));
    //     });
    //   }
    async deletePersonnel(adminId) {
      if (!confirm('確定要刪除此人員嗎？')) return;

      try {
        const response = await axios.post(
          getApiUrl(API_PATHS.ADMIN_DELETE),
          { id: adminId },
          {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          alert('人員已成功刪除');
          this.fetchAdmins();  // 重新获取客户列表
        } else {
          throw new Error(response.data.message || '刪除人員失敗');
        }
      } catch (error) {
        console.error('Error deleting customer:', error);
        alert('刪除人員失敗：' + (error.response?.data?.message || error.message));
      }
    },
    editPersonnel(adminId) {
      this.$router.push({
        name: 'AddPersonnel',
        query: { id: adminId }
      });
    },
    async fetchAdmins() {
      try {
        const response = await axios.post(getApiUrl(API_PATHS.ADMIN_LIST), {}, {
          withCredentials: true
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
        alert('獲取管理員列表失敗：' + (error.response?.data?.message || error.message));
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

/* 所有其他樣式已移至 unified-base */
.edit-btn, .delete-btn {
  padding: 4px 8px;
  margin: 0 4px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.edit-btn {
  background-color: #4CAF50;
  color: white;
}

.edit-btn:hover {
  background-color: #45a049;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.delete-btn:hover {
  background-color: #da190b;
}
</style>
