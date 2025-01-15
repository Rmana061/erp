<!-- 客戶登入 -->
<template>
  <body class="customer-mode">
  <div class="login-container">
    <div class="login-box">
      <h2>客戶登入</h2>
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
  name: 'CustomerLogin',
  data() {
    return {
      username: '',
      password: '',
      isMenuOpen: false
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/customer-login', {
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
          sessionStorage.setItem('isCustomerAuthenticated', 'true');
          sessionStorage.setItem('customerId', response.data.customer_id);
          // 登入成功後導向客戶首頁
          this.$router.push('/customer-homepage');
        }
      } catch (error) {
        console.error('Login error:', error);
        alert('登入失敗：帳號或密碼錯誤');
      }
    },
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
      document.body.style.overflow = this.isMenuOpen ? 'hidden' : '';
    },
    closeMenu() {
      this.isMenuOpen = false;
      document.body.style.overflow = '';
    }
  },
  watch: {
    $route() {
      this.closeMenu();
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
