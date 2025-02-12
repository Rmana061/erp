import axiosInstance from '../config/axios';
import { setUserPermissions } from '../utils/permissionUtils';
import { API_PATHS } from '../config/api';

export const adminMixin = {
  data() {
    return {
      adminName: '',
      adminId: null,
      permissions: {}
    };
  },
  methods: {
    async fetchAdminInfo() {
      try {
        console.log('開始獲取管理員信息...');
        // 檢查本地存儲中是否有 admin_id
        const adminId = localStorage.getItem('admin_id');
        if (!adminId) {
          console.log('未找到 admin_id，重定向到登入頁面');
          this.$router.push('/admin-login');
          return;
        }

        // 嘗試從 sessionStorage 獲取
        const adminInfo = sessionStorage.getItem('adminInfo');
        if (adminInfo) {
          const parsedInfo = JSON.parse(adminInfo);
          console.log('從 sessionStorage 獲取的管理員信息:', parsedInfo);
          if (parsedInfo.admin_name && parsedInfo.permissions) {
            this.adminName = parsedInfo.admin_name;
            this.adminId = adminId;
            console.log('設置權限從 sessionStorage:', parsedInfo.permissions);
            setUserPermissions(parsedInfo.permissions);
            this.permissions = parsedInfo.permissions;
            return;
          }
        }

        // 如果 sessionStorage 中沒有，則從 API 獲取
        console.log('從 API 獲取管理員信息...');
        const response = await axiosInstance.post(API_PATHS.ADMIN_INFO);

        console.log('API 響應:', response.data);

        if (response.data.status === 'success') {
          const { admin_name, permissions } = response.data.data;
          this.adminName = admin_name;
          this.adminId = adminId;
          
          console.log('設置權限從 API:', permissions);
          setUserPermissions(permissions);
          this.permissions = permissions;
          
          // 更新 sessionStorage
          sessionStorage.setItem('adminInfo', JSON.stringify(response.data.data));
        } else {
          throw new Error(response.data.message || '獲取管理員信息失敗');
        }
      } catch (error) {
        console.error('獲取管理員信息錯誤:', error);
        if (error.response?.status === 401) {
          // 如果未登錄或登錄過期，清除存儲並重定向到登錄頁面
          localStorage.removeItem('admin_id');
          sessionStorage.removeItem('adminInfo');
          this.$router.push('/admin-login');
        }
      }
    }
  },
  created() {
    console.log('adminMixin created, 調用 fetchAdminInfo');
    this.fetchAdminInfo();
  }
}; 