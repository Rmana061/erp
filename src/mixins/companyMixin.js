import axios from 'axios';

export const companyMixin = {
  data() {
    return {
      companyName: ''
    };
  },
  methods: {
    async fetchCompanyInfo() {
      try {
        // 首先尝试从 sessionStorage 获取
        const userInfo = sessionStorage.getItem('userInfo');
        if (userInfo) {
          const parsedInfo = JSON.parse(userInfo);
          if (parsedInfo.company_name) {
            this.companyName = parsedInfo.company_name;
            return;
          }
        }

        // 如果 sessionStorage 中没有，则从 API 获取
        const response = await axios.get('http://127.0.0.1:5000/api/customer/info', {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          this.companyName = response.data.data.company_name;
          // 更新 sessionStorage
          sessionStorage.setItem('userInfo', JSON.stringify(response.data.data));
        }
      } catch (error) {
        console.error('Error fetching company info:', error);
        if (error.response?.status === 401) {
          // 如果未登录或登录过期，重定向到登录页面
          this.$router.push('/customer-login');
        }
      }
    }
  },
  created() {
    this.fetchCompanyInfo();
  }
}; 