import axios from 'axios';
import { API_PATHS, getApiUrl } from '../config/api';

export const logoutMixin = {
  methods: {
    logout() {
      // 根据当前路由路径判断用户类型
      const isAdmin = this.$route.path.indexOf('admin') !== -1 || 
                      !this.$route.path.startsWith('/') ||
                      ['/today-orders', '/all-orders', '/customer-management', '/product-management', '/notification-setting'].includes(this.$route.path);
      
      // 确认是否登出
      if (!confirm('確定要登出嗎？')) {
        return;
      }
      
      // 发送登出请求
      axios.post(getApiUrl(API_PATHS.LOGOUT), {}, { withCredentials: true })
        .then(() => {
          console.log('成功登出');
          // 清除本地存储
          localStorage.removeItem('customer_id');
          localStorage.removeItem('company_name');
          sessionStorage.removeItem('userInfo');
          sessionStorage.removeItem('isCustomerAuthenticated');
          
          if (isAdmin) {
            sessionStorage.removeItem('adminInfo');
            this.$router.push('/admin-login');
          } else {
            this.$router.push('/customer-login');
          }
        })
        .catch(error => {
          console.error('登出錯誤:', error);
          
          // 即使请求出错，仍然清除本地存储并重定向
          localStorage.removeItem('customer_id');
          localStorage.removeItem('company_name');
          sessionStorage.removeItem('userInfo');
          sessionStorage.removeItem('isCustomerAuthenticated');
          
          if (isAdmin) {
            sessionStorage.removeItem('adminInfo');
            this.$router.push('/admin-login');
          } else {
            this.$router.push('/customer-login');
          }
        });
    }
  }
}; 