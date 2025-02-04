import { createRouter, createWebHistory } from 'vue-router';

// Import your views
import Admin from '../views/Admin.vue';
import AllOrders from '../views/AllOrders.vue';
import CustomerManagement from '../views/CustomerManagement.vue';
import NotificationSetting from '../views/NotificationSetting.vue';
import ProductManagement from '../views/ProductManagement.vue';
import TodayOrders from '../views/TodayOrders.vue';
import AccountSettings from '../views/2AccountSettings.vue';    
import AddPersonnel from '../views/AddPersonnel.vue';
import AddCustomer from '../views/AddCustomer.vue';
import AddProduct from '../views/AddProduct.vue';
import AddOrderPlanB from '../views/2AddOrderPlanB.vue';        
import ProductList from '../views/2ProductList.vue';            
import OrderSystem from '../views/2OrderSystem.vue';            
import OrderRecord from '../views/2OrderRecord.vue';            
import AdminLogin from '../views/AdminLogin.vue';
import CustomerLogin from '../views/2CustomerLogin.vue';
import LineBinding from '../views/LineBinding.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/admin-login'
    },
    {
      path: '/admin-login',
      name: 'AdminLogin',
      component: AdminLogin
    },
    {
      path: '/today-orders',
      name: 'TodayOrders',
      component: TodayOrders,
      meta: { requiresAuth: true }
    },
    {
      path: '/all-orders',
      name: 'AllOrders',
      component: AllOrders,
      meta: { requiresAuth: true }
    },
    {
      path: '/customer-management',
      name: 'CustomerManagement',
      component: CustomerManagement,
      meta: { requiresAuth: true }
    },
    {
      path: '/product-management',
      name: 'ProductManagement',
      component: ProductManagement,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'Admin',
      component: Admin,
      meta: { requiresAuth: true }
    },
    {
      path: '/notification-setting',
      name: 'NotificationSetting',
      component: NotificationSetting,
      meta: { requiresAuth: true }
    },
    {
      path: '/add-personnel',
      name: 'AddPersonnel',
      component: AddPersonnel,
      meta: { requiresAuth: true }
    },
    {
      path: '/add-customer',
      name: 'AddCustomer',
      component: AddCustomer,
      meta: { requiresAuth: true }
    },
    {
      path: '/add-product',
      name: 'AddProduct',
      component: AddProduct,
      meta: { requiresAuth: true }
    },
    {
      path: '/customer-login',
      name: 'CustomerLogin',
      component: CustomerLogin
    },
    {
      path: '/account-settings',
      name: 'AccountSettings',
      component: AccountSettings,
      meta: { requiresCustomerAuth: true }
    },
    {
      path: '/add-order-plan-b',
      name: 'AddOrderPlanB',
      component: AddOrderPlanB,
      meta: { requiresCustomerAuth: true }
    },
    {
      path: '/order-system',
      name: 'OrderSystem',
      component: OrderSystem,
      meta: { requiresCustomerAuth: true }
    },
    {
      path: '/order-record',
      name: 'OrderRecord',
      component: OrderRecord,
      meta: { requiresCustomerAuth: true }
    },
    {
      path: '/product-list',
      name: 'ProductList',
      component: ProductList,
      meta: { requiresCustomerAuth: true }
    },
    {
      path: '/line-binding',
      name: 'LineBinding',
      component: LineBinding
    }
  ]
});

// 修改路由守衛
router.beforeEach((to, from, next) => {
  // 根據路由設置標題
  if (to.matched.some(record => record.meta.requiresAuth)) {
    document.title = '管理者系統';
  } else if (to.matched.some(record => record.meta.requiresCustomerAuth)) {
    document.title = '客戶系統';
  } else if (to.path === '/admin-login') {
    document.title = '管理者系統';
  } else if (to.path === '/customer-login') {
    document.title = '客戶系統';
  } else {
    document.title = 'ERP系統';
  }

  // 檢查登入狀態
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const isAuthenticated = sessionStorage.getItem('isAuthenticated');
    if (!isAuthenticated) {
      next({
        path: '/admin-login',
        query: { redirect: to.fullPath }
      });
    } else {
      next();
    }
  } else if (to.matched.some(record => record.meta.requiresCustomerAuth)) {
    const isCustomerAuthenticated = sessionStorage.getItem('isCustomerAuthenticated');
    if (!isCustomerAuthenticated) {
      next({
        path: '/customer-login',
        query: { redirect: to.fullPath }
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
