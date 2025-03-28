// API配置文件
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

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
    CHECK_RECENT_ORDER: '/api/orders/check-recent',
    UPDATE_ORDER_STATUS: '/api/orders/update-status',
    BATCH_UPDATE_ORDER_STATUS: '/api/orders/batch-update-status',
    UPDATE_ORDER_CONFIRMED: '/api/orders/update-confirmed',
    UPDATE_ORDER_SHIPPED: '/api/orders/update-shipped',
    CANCEL_ORDER: '/api/orders/cancel',
    UPDATE_ORDER_QUANTITY: '/api/orders/update-quantity',
    
    // 产品相关
    LOGIN: '/api/login',
    LOGOUT: '/api/logout',
    PRODUCTS: '/api/products/list',
    PRODUCT_ADD: '/api/products/add',
    PRODUCT_UPDATE: (id) => `/api/products/update/${id}`,
    PRODUCT_DELETE: (id) => `/api/products/delete/${id}`,
    PRODUCT_DETAIL: (id) => `/api/products/${id}/detail`,
    VIEWABLE_PRODUCTS: '/api/products/viewable',
    LOCKED_DATES: '/api/products/locked-dates',
    LOCK_DATE: '/api/products/lock-date',
    UNLOCK_DATE: '/api/products/unlock-date',
    
    // 客户相关
    CUSTOMER_LIST: '/api/customer/list',
    CUSTOMER_ADD: '/api/customer/add',
    CUSTOMER_UPDATE: '/api/customer/update',
    CUSTOMER_DELETE: '/api/customer/delete',
    CUSTOMER_INFO: '/api/customer/info',
    CUSTOMER_DETAIL: (id) => `/api/customer/${id}/info`,
    UPDATE_CUSTOMER_INFO: '/api/customer/update-self',
    
    // LINE相关
    GENERATE_BIND_URL: '/api/line/generate-bind-url',
    BIND_LINE: '/api/line/bind',
    UNBIND_LINE: '/api/line/unbind',
    UNBIND_LINE_USER: '/api/line/unbind-user',
    UNBIND_LINE_GROUP: '/api/line/unbind-group',
    LINE_CALLBACK: '/api/line/line-binding',
    
    // 管理员相关
    ADMIN_LIST: '/api/admin/list',
    ADMIN_ADD: '/api/admin/add',
    ADMIN_UPDATE: '/api/admin/update',
    ADMIN_DELETE: '/api/admin/delete',
    ADMIN_INFO: '/api/admin/info',
    ADMIN_DETAIL: (id) => `/api/admin/info/${id}`,
    
    // 文件上传
    UPLOAD_IMAGE: '/api/upload/image',
    UPLOAD_DOCUMENT: '/api/upload/document',
    
    // 日誌相關
    LOG_RECORDS: '/api/log/logs',
    LOG_STATS: '/api/log/logs/stats',
    LOG_RECORD: '/api/log/record'
};

// 完整API URL生成函数
export const getApiUrl = (path) => {
    // 如果path是函数（用于带参数的路径），先执行它
    if (typeof path === 'function') {
        return `${API_BASE_URL}${path()}`;
    }
    return `${API_BASE_URL}${path}`;
}; 