import axios from 'axios';
import { API_BASE_URL } from './api';

// 创建 axios 实例
const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,  // 允许跨域请求携带 cookies
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// 请求拦截器
axiosInstance.interceptors.request.use(
    config => {
        const adminId = localStorage.getItem('admin_id');
        if (adminId) {
            config.headers['Authorization'] = `Bearer ${adminId}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        if (error.response?.status === 401) {
            // 清除本地存储的认证信息
            localStorage.removeItem('admin_id');
            sessionStorage.removeItem('adminInfo');
            // 使用 router 进行导航
            window.location.href = '/admin-login';
        }
        return Promise.reject(error);
    }
);

export default axiosInstance; 