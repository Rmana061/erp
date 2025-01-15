<!-- 側邊欄組件 -->
<template>
  <div class="sidebar-container">
    <!-- 書籤式選單按鈕（僅在小屏幕顯示） -->
    <button class="bookmark-toggle" :class="[{ active: isMenuOpen }, menuTypeClass]" @click="toggleMenu">
      <span class="bookmark-text">選單</span>
    </button>

    <!-- 遮罩層 -->
    <div class="menu-overlay" :class="{ active: isMenuOpen }" @click="closeMenu"></div>

    <!-- 側邊欄 -->
    <div class="sidebar" :class="[{ active: isMenuOpen }, menuTypeClass]">
      <ul class="menu">
        <li v-for="item in menuItems" :key="item.path" 
            :class="['menu-item', { active: isActive(item.path) }]">
          <router-link :to="item.path" class="menu-item">{{ item.name }}</router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SideBaradmin',
  props: {
    menuType: {
      type: String,
      required: true,
      validator: value => ['customer', 'admin'].includes(value)
    }
  },
  data() {
    return {
      isMenuOpen: false,
      customerMenu: [
        { path: '/customer-homepage', name: '首頁' },
        { path: '/order-system', name: '訂貨系統' },
        { path: '/order-record', name: '訂貨紀錄' },
        { path: '/product-list', name: '產品一覽' },
        { path: '/account-settings', name: '帳號設定' }
      ],
      adminMenu: [
        { path: '/today-orders', name: '今日訂單' },
        { path: '/all-orders', name: '所有訂單' },
        { path: '/customer-management', name: '客戶管理' },
        { path: '/product-management', name: '產品管理' },
        { path: '/admin', name: '管理員' },
        { path: '/notification-setting', name: '通知設定' }
      ]
    }
  },
  computed: {
    menuItems() {
      return this.menuType === 'customer' ? this.customerMenu : this.adminMenu
    },
    menuTypeClass() {
      return this.menuType === 'customer' ? 'customer-theme' : 'admin-theme'
    }
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
      document.body.style.overflow = this.isMenuOpen ? 'hidden' : '';
    },
    closeMenu() {
      this.isMenuOpen = false;
      document.body.style.overflow = '';
    },
    isActive(path) {
      return this.$route.path === path
    }
  },
  watch: {
    $route() {
      this.closeMenu();
    }
  }
}
</script>

<style>
/* 其他通用樣式保持在基礎樣式文件中 */
</style> 

