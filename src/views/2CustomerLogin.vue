<!-- 客戶登入 -->
<template>
  <body class="customer-mode">
  <div class="container">
    <div class="login-container">
      <div class="login-box">
        <h2>客戶登入</h2>
        <form class="login-form" @submit.prevent="handleLogin">
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
          <button type="submit" class="login-button" :disabled="isLoading">
            {{ isLoading ? '登錄中...' : '登入' }}
          </button>
        </form>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  setup() {
    const router = useRouter();
    const loginForm = ref({
      account: '',
      password: ''
    });
    const isMenuOpen = ref(false);
    const isLoading = ref(false);

    const handleLogin = async () => {
      if (isLoading.value) return;
      isLoading.value = true;
      
      try {
        console.log('正在尝试登录，用户名:', loginForm.value.account);
        const response = await axios.post(
          getApiUrl(API_PATHS.CUSTOMER_LOGIN),
          {
            username: loginForm.value.account,
            password: loginForm.value.password
          },
          {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        console.log('登录响应:', response.data);
        
        if (response.data.status === 'success') {
          // 保存用户信息到 localStorage 和 sessionStorage
          const userData = response.data.data;
          console.log('保存用户数据:', userData);
          
          // 确保存储客户ID和公司名称到localStorage
          localStorage.setItem('customer_id', userData.customer_id);
          localStorage.setItem('company_name', userData.company_name || ''); // 确保公司名不为null
          
          // 同时保存到sessionStorage作为备份
          sessionStorage.setItem('userInfo', JSON.stringify({
            customer_id: userData.customer_id,
            username: userData.username,
            company_name: userData.company_name
          }));
          sessionStorage.setItem('isCustomerAuthenticated', 'true');
          
          // 检查是否有之前保存的重定向页面
          const redirectPath = localStorage.getItem('redirect_after_login');
          if (redirectPath) {
            localStorage.removeItem('redirect_after_login');
            console.log('正在重定向到:', redirectPath);
            router.push(redirectPath);
          } else {
            // 直接跳转到订单系统
            router.push('/order-system');
          }
        } else {
          alert(response.data.message || '登入失敗');
        }
      } catch (error) {
        console.error('登录错误:', error);
        console.error('错误响应:', error.response?.data);
        alert(error.response?.data?.message || '登入失敗，請稍後再試');
      } finally {
        isLoading.value = false;
      }
    };

    const toggleMenu = () => {
      isMenuOpen.value = !isMenuOpen.value;
      document.body.style.overflow = isMenuOpen.value ? 'hidden' : '';
    };

    const closeMenu = () => {
      isMenuOpen.value = false;
      document.body.style.overflow = '';
    };

    return {
      loginForm,
      isMenuOpen,
      isLoading,
      handleLogin,
      toggleMenu,
      closeMenu
    };
  }
};
</script>

<style scoped>
@import '../assets/styles/unified-base.css';

.login-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
