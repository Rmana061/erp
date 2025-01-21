<!-- 通知設定 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,</span>
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
import { adminMixin } from '../mixins/adminMixin';
import { timeMixin } from '../mixins/timeMixin';
import SideBar from '../components/SideBar.vue';

export default {
  name: 'NotificationSetting',
  mixins: [adminMixin, timeMixin],
  components: {
    SideBar
  },
  mounted() {
    document.title = '管理者系統';
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有樣式已移至 unified-base */
</style>