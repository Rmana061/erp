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
            <button class="action-button" @click="deletePersonnel">- 刪除人員</button>
            <button class="action-button" @click="editPersonnel">+ 編輯人員</button>
          </div>

          <div class="table-container">
            <table class="admin-list">
              <thead>
                <tr>
                  <th>選擇</th>
                  <th>帳號</th>
                  <th>姓名</th>
                  <th>工號</th>
                  <th>權限等級</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(admin, index) in admins" :key="admin.id">
                  <td @click="toggleSelection(index)">{{ admin.selected ? '■' : '□' }}</td>
                  <td>{{ admin.account }}</td>
                  <td>{{ admin.name }}</td>
                  <td>{{ admin.staff_no }}</td>
                  <td>{{ admin.permission_level }}</td>
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

export default {
  name: 'Admin',
  mixins: [adminMixin],
  components: {
    SideBar
  },
  data() {
    return {
      currentTime: '',
      admins: []
    };
  },
  methods: {
    updateCurrentTime() {
      const now = new Date();
      const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        weekday: 'long', 
        hour: '2-digit', 
        minute: '2-digit', 
        hour12: false 
      };
      this.currentTime = now.toLocaleString('zh-TW', options)
        .replace(/\//g, '/')
        .replace('星期', ' 星期')
        .replace(/(\d+):(\d+)/, '$1:$2');
    },
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
    deletePersonnel() {
      const selectedAdmins = this.admins.filter(admin => admin.selected);
      
      if (selectedAdmins.length === 0) {
        alert('請選擇要刪除的人員');
        return;
      }

      if (confirm(`確定要刪除選中的 ${selectedAdmins.length} 位人員嗎？`)) {
        const deletePromises = selectedAdmins.map(admin =>
          axios.delete(`http://127.0.0.1:5000/api/admin/delete`, {
            data: { id: admin.id },
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          })
        );

        Promise.all(deletePromises)
          .then(responses => {
            const hasError = responses.some(response => response.data.status !== 'success');
            if (hasError) {
              throw new Error('部分人員刪除失敗');
            }
            this.fetchAdmins();
            alert('人員已成功刪除');
          })
          .catch(error => {
            console.error('Error deleting admins:', error);
            alert('刪除人員時發生錯誤：' + (error.response?.data?.message || error.message));
          });
      }
    },
    editPersonnel() {
      const selectedAdmins = this.admins.filter(admin => admin.selected);
      
      if (selectedAdmins.length !== 1) {
        alert('請選擇一位要編輯的人員');
        return;
      }

      this.$router.push({
        name: 'AddPersonnel',
        query: { id: selectedAdmins[0].id }
      });
    },
    toggleSelection(index) {
      this.admins[index].selected = !this.admins[index].selected;
    },
    async fetchAdmins() {
      try {
        const response = await axios.get('http://localhost:5000/api/admin/list', {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.data.status === 'success') {
          this.admins = response.data.data.map(admin => ({
            id: admin.id,
            account: admin.admin_account,
            name: admin.admin_name,
            staff_no: admin.staff_no || '-',
            permission_level: this.getPermissionName(admin.permission_level_id),
            selected: false
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
    this.updateCurrentTime();
    this.timeInterval = setInterval(this.updateCurrentTime, 60000);
    document.title = '管理者系統';
    this.fetchAdmins();
  },
  beforeUnmount() {
    clearInterval(this.timeInterval);
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
