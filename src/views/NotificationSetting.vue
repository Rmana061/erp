<!-- 通知設定 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi Sales01</span>
        <span>{{ currentTime }}</span>
      </div>
      
      <h2>通知設定</h2>
      <div class="notification-box">
        <h3>訂單成功通知：</h3>
        <p>Hi _____</p>
        <p>訂單_____ 已確認，預計1~2 工作天內出貨。</p>
      </div>
      <div class="notification-box" style="background-color: #FFEBEE;">
        <h3>訂單失敗通知：</h3>
        <p>Hi _____</p>
        <p>訂單_____ 未通過，再請確認修正。</p>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import SideBar from '../components/SideBar.vue';

export default {
  name: 'NotificationSetting',
  components: {
    SideBar
  },
  mounted() {
    document.title = '管理者系統'; // 設置頁面標題
  },
  data() {
    return {
      isMenuOpen: false,
      currentTime: ''
    };
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
    updateCurrentTime() {
      const now = new Date();
      const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        weekday: 'long', 
        hour: '2-digit', 
        minute: '2-digit', 
        hour12: false 
      };
      this.currentTime = now.toLocaleString('zh-TW', options)
        .replace(/\//g, '/')
        .replace('星期', ' 星期')
        .replace(/(\d+):(\d+)/, '$1:$2');
    },
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    }
  },
  mounted() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
  },
  watch: {
    $route() {
      this.closeMenu();
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>