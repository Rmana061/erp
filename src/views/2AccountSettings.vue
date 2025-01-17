<!-- 帳號設定 -->
<template>
  <body class="customer-mode">
  <div class="container">
    <SideBar menu-type="customer" />
    
    <div class="main-content">
      <div class="header">
        <span>Hi {{ companyName }}您好,</span>
        <span>{{ currentTime }}</span>
      </div>
      
      <div class="content-wrapper">
        <div class="page-header">
          <h2>帳號設定</h2>
        </div>

        <div class="account-info">
          <div class="info-grid">
            <p><strong>公司名稱：</strong></p>
            <p>A公司（客戶無法更改）</p>
            <p><strong>帳號：</strong></p>
            <p>A公司（客戶無法更改）</p>
            <p><strong>密碼：</strong></p>
            <p>12345678</p>
          </div>
          <div class="line-settings">
            <p><strong>LINE帳號綁定</strong></p>
            <div class="line-buttons">
              <button @click="bindAccount">綁定帳號</button>
              <button @click="unbindAccount">解除綁定</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import { timeMixin } from '../mixins/timeMixin';
import { companyMixin } from '../mixins/companyMixin';
import SideBar from '../components/SideBar.vue';
import axios from 'axios';

export default {
  name: 'AccountSettings',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  methods: {
    bindAccount() {
      alert('綁定帳號功能');
    },
    unbindAccount() {
      alert('解除綁定功能');
    }
  },
  mounted() {
    document.title = '客戶系統';
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
