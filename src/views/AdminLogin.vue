<!-- 管理者登入 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <div class="login-container">
      <div class="login-box">
        <h2>管理者系統</h2>
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
          <button type="submit" class="login-button">登入</button>
        </form>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axiosInstance from '../config/axios';
import { API_PATHS } from '../config/api';

export default {
  setup() {
    const router = useRouter();
    const loginForm = ref({
      account: '',
      password: ''
    });
    const isMenuOpen = ref(false);

    const handleLogin = async () => {
      try {
        console.log('开始登录...');
        const response = await axiosInstance.post(
          API_PATHS.ADMIN_LOGIN,
          {
            admin_account: loginForm.value.account,
            admin_password: loginForm.value.password
          }
        );

        console.log('登录响应:', response.data);
        if (response.data.status === 'success') {
          // 保存登录信息
          const adminData = response.data.data;
          localStorage.setItem('admin_id', adminData.id);
          sessionStorage.setItem('adminInfo', JSON.stringify({
            id: adminData.id,
            admin_account: adminData.admin_account,
            admin_name: adminData.admin_name,
            staff_no: adminData.staff_no,
            permission_level_id: adminData.permission_level_id,
            permissions: adminData.permissions
          }));
          
          // 设置认证标志
          sessionStorage.setItem('isAuthenticated', 'true');
          
          console.log('准备跳转页面...');
          // 使用 router.push 进行导航
          try {
            await router.push({ name: 'TodayOrders' });
          } catch (navigationError) {
            console.error('Navigation error:', navigationError);
            // 如果路由导航失败，使用 window.location
            window.location.href = '/today-orders';
          }
        } else {
          alert(response.data.message || '登入失敗');
        }
      } catch (error) {
        console.error('Login error:', error);
        alert(error.response?.data?.message || '登入失敗，請稍後再試');
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
      handleLogin,
      toggleMenu,
      closeMenu
    };
  }
};
</script>

<style scoped>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
