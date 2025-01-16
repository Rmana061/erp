<!-- 管理者登入 -->
<template>
  <body class="admin-mode">
    <div class="login-container">
      <div class="login-box">
        <h2>管理者登入</h2>
        <form @submit.prevent="handleLogin">
          <div class="input-group">
            <label>帳號：</label>
            <input type="text" v-model="username" required>
          </div>
          <div class="input-group">
            <label>密碼：</label>
            <input type="password" v-model="password" required>
          </div>
          <button type="submit" class="login-button">登入</button>
        </form>
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
      username: '',
      password: ''
    };
  },
  mounted() {
    document.title = '管理者系統';
  },
  beforeUnmount() {
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/login', {
          username: this.username,
          password: this.password
        }, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (response.data.message === 'Login successful') {
          // 設置登入狀態
          sessionStorage.setItem('isAuthenticated', 'true');
          // 登入成功後導向今日訂單頁面
          this.$router.push('/today-orders');
        }
      } catch (error) {
        console.error('Login error:', error);
        alert('登入失敗：帳號或密碼錯誤');
      }
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
