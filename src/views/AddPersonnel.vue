<!-- 新增人員 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi Sales01</span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
          <h2>管理員（新增人員）</h2>
          <div class="action-buttons">
            <button class="action-button" @click="updatePersonnel">+ 更新</button>
            <button class="action-button cancel" @click="navigateTo('Admin')">- 取消</button>
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

export default {
  name: 'AddPersonnel',
  components: {
    SideBar
  },
  data() {
    return {
      currentTime: '',
      personnelAccount: '',
      personnelPassword: '',
      personnelName: '',
      personnelStaffNo: '',
      personnelPermission: ''
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
    async updatePersonnel() {
      if (!this.personnelAccount || !this.personnelPassword || !this.personnelName || !this.personnelStaffNo || !this.personnelPermission) {
        alert('請填寫所有必要欄位');
        return;
      }

      const permissionMap = {
        '最高權限': 1,
        '普通權限': 2,
        '基本權限': 3,
        '檢視權限': 4
      };

      try {
        const response = await axios.post('http://127.0.0.1:5000/api/admins', {
          admin_account: this.personnelAccount,
          admin_password: this.personnelPassword,
          admin_name: this.personnelName,
          staff_no: this.personnelStaffNo,
          permission_level_id: permissionMap[this.personnelPermission],
          status: 'active'
        }, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (response.data) {
          alert('人員新增成功！');
          this.$router.push('/admin');
        }
      } catch (error) {
        console.error('Error adding personnel:', error);
        alert('新增失敗：' + (error.response?.data?.error || error.message));
      }
    }
  },
  mounted() {
    this.updateCurrentTime();
    this.timeInterval = setInterval(this.updateCurrentTime, 60000);
    document.title = '管理者系統';
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
