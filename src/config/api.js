// API配置文件
export const API_BASE_URL = 'https://0406-111-249-201-90.ngrok-free.app';

// API路径配置
export const API_PATHS = {
    // 认证相关
    ADMIN_LOGIN: '/api/admin-login',
    CUSTOMER_LOGIN: '/api/customer-login',
    LOGOUT: '/api/auth/logout',
    
    // 订单相关
    ORDERS: '/api/orders/list',
    ORDERS_ALL: '/api/orders/all',
    PENDING_ORDERS: '/api/orders/pending',
    CREATE_ORDER: '/api/orders/create',
    UPDATE_ORDER_STATUS: '/api/orders/update-status',
    UPDATE_ORDER_CONFIRMED: '/api/orders/update-confirmed',
    UPDATE_ORDER_SHIPPED: '/api/orders/update-shipped',
    CANCEL_ORDER: '/api/orders/cancel',
    
    // 产品相关
    PRODUCTS: '/api/products',
    PRODUCT_DETAIL: (id) => `/api/products/${id}`,
    PRODUCT_UPDATE: (id) => `/api/products/${id}`,
    PRODUCT_DELETE: (id) => `/api/products/${id}`,
    VIEWABLE_PRODUCTS: '/api/products/viewable',
    
    // 客户相关
    CUSTOMER_LIST: '/api/customer/list',
    CUSTOMER_ADD: '/api/customer/add',
    CUSTOMER_UPDATE: '/api/customer/update',
    CUSTOMER_DELETE: '/api/customer/delete',
    CUSTOMER_INFO: '/api/customer/info',
    CUSTOMER_DETAIL: (id) => `/api/customer/${id}/info`,
    
    // 管理员相关
    ADMIN_LIST: '/api/admin/list',
    ADMIN_ADD: '/api/admin/add',
    ADMIN_UPDATE: '/api/admin/update',
    ADMIN_DELETE: '/api/admin/delete',
    ADMIN_INFO: '/api/admin/info',
    ADMIN_DETAIL: (id) => `/api/admin/info/${id}`,
    
    // 文件上传
    UPLOAD_IMAGE: '/api/upload/image',
    UPLOAD_DOCUMENT: '/api/upload/document'
};

// 完整API URL生成函数
export const getApiUrl = (path) => {
    // 如果path是函数（用于带参数的路径），先执行它
    if (typeof path === 'function') {
        return `${API_BASE_URL}${path()}`;
    }
    return `${API_BASE_URL}${path}`;
}; 