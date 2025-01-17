import axios from 'axios';

export const adminMixin = {
  data() {
    return {
      adminName: ''
    };
  },
  methods: {
    async fetchAdminInfo() {
      try {
        // 检查本地存储中是否有 admin_id
        const adminId = localStorage.getItem('admin_id');
        if (!adminId) {
          console.log('No admin_id found in localStorage');
          this.$router.push('/admin-login');
          return;
        }

        // 尝试从 sessionStorage 获取
        const adminInfo = sessionStorage.getItem('adminInfo');
        if (adminInfo) {
          const parsedInfo = JSON.parse(adminInfo);
          if (parsedInfo.admin_name) {
            this.adminName = parsedInfo.admin_name;
            return;
          }
        }

        // 如果 sessionStorage 中没有，则从 API 获取
        const response = await axios.get('http://127.0.0.1:5000/api/admin/info', {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          this.adminName = response.data.data.admin_name;
          // 更新 sessionStorage
          sessionStorage.setItem('adminInfo', JSON.stringify(response.data.data));
        }
      } catch (error) {
        console.error('Error fetching admin info:', error);
        if (error.response?.status === 401) {
          // 如果未登录或登录过期，清除存储并重定向到登录页面
          localStorage.removeItem('admin_id');
          sessionStorage.removeItem('adminInfo');
          this.$router.push('/admin-login');
        }
      }
    }
  },
  created() {
    this.fetchAdminInfo();
  }
}; 