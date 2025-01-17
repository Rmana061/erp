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
        const response = await axios.post('http://localhost:5000/api/customer-login', {
          username: this.username,
          password: this.password
        }, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          // 保存用户信息到 localStorage 和 sessionStorage
          localStorage.setItem('customer_id', response.data.data.customer_id);
          
          // 获取完整的用户信息
          const userInfoResponse = await axios.get(`http://localhost:5000/api/customer/${response.data.data.customer_id}/info`, {
            withCredentials: true
          });
          
          if (userInfoResponse.data.status === 'success') {
            sessionStorage.setItem('userInfo', JSON.stringify(userInfoResponse.data.data));
            sessionStorage.setItem('isCustomerAuthenticated', 'true');
            this.$router.push('/customer-homepage');
          } else {
            throw new Error('Failed to get user info');
          }
        } else {
          alert(response.data.message || '登入失敗');
        }
      } catch (error) {
        console.error('Login error:', error);
        alert(error.response?.data?.message || '登入失敗，請稍後再試');
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
