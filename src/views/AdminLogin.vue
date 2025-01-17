<!-- 管理者登入 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <div class="login-container">
      <div class="login-box">
        <h2>管理者系統</h2>
        <form class="login-form" @submit.prevent="submitForm">
          <div class="form-group">
            <label for="account">帳號</label>
            <input 
              type="text" 
              id="account"
              v-model="loginForm.account"
              required>
          </div>
          <div class="form-group">
            <label for="password">密碼</label>
            <input 
              type="password" 
              id="password"
              v-model="loginForm.password"
              required>
          </div>
          <button type="submit" class="login-button">登入</button>
        </form>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminLogin',
  data() {
    return {
      loginForm: {
        account: '',
        password: ''
      }
    };
  },
  methods: {
    async submitForm() {
      try {
        const response = await axios.post(
          'http://127.0.0.1:5000/api/admin-login',
          {
            admin_account: this.loginForm.account,
            admin_password: this.loginForm.password
          },
          {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          // 保存登录信息
          localStorage.setItem('admin_id', response.data.data.id);
          sessionStorage.setItem('adminInfo', JSON.stringify({
            id: response.data.data.id,
            admin_account: response.data.data.admin_account,
            admin_name: response.data.data.admin_name,
            staff_no: response.data.data.staff_no,
            permission_level_id: response.data.data.permission_level_id
          }));
          sessionStorage.setItem('isAuthenticated', 'true');

          // 使用 Vue Router 进行导航
          this.$router.push({ name: 'TodayOrders' });
        } else {
          alert(response.data.message || '登入失敗');
        }
      } catch (error) {
        console.log('Login error:', error);
        alert(error.response?.data?.message || '登入失敗，請稍後再試');
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
