<!-- 新增客戶 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi Sales01</span>
        <span>{{ currentTime }}</span>
      </div>
      
      <h2>{{ isEditing ? '編輯客戶' : '新增客戶' }}</h2>
      <form @submit.prevent="submitCustomer">
        <div class="form-container">
          <div class="form-group">
            <label>公司名稱：</label>
            <input type="text" v-model="newCustomer.companyName" placeholder="（管理員自填）">
          </div>
          <div class="form-group">
            <label>帳號：</label>
            <input type="text" v-model="newCustomer.account" placeholder="（管理員自填）">
          </div>
          <div class="form-group">
            <label>密碼：</label>
            <input type="password" v-model="newCustomer.password" placeholder="（管理員自填）">
          </div>
          <div class="form-group">
            <label>可購產品：</label>
            <div class="checkbox-group">
              <label v-for="(product, index) in products" :key="index" class="custom-checkbox">
                <input type="checkbox" v-model="newCustomer.selectedProducts" :value="product.value">
                <span class="checkmark"></span>
                {{ product.name }}
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>LINE帳號綁定：</label>
            <input type="text" v-model="newCustomer.lineAccount" placeholder="">
          </div>
          <div class="form-group">
            <label>聯絡人：</label>
            <input type="text" v-model="newCustomer.contactPerson" placeholder="請輸入聯絡人姓名">
          </div>
          <div class="form-group">
            <label>電話：</label>
            <input type="tel" v-model="newCustomer.phone" placeholder="請輸入聯絡電話">
          </div>
          <div class="form-group">
            <label>Email：</label>
            <input type="email" v-model="newCustomer.email" placeholder="請輸入電子郵件地址">
          </div>
          <div class="form-group">
            <label>地址：</label>
            <input type="text" v-model="newCustomer.address" placeholder="請輸入完整地址">
          </div>
          <div class="form-group">
            <label>備註：</label>
            <textarea v-model="newCustomer.notes" placeholder="請輸入其他相關備註"></textarea>
          </div>
        </div>
      </form>
    </div>
  </div>
  </body>
</template>

<script>
import axios from 'axios';
import SideBar from '../components/SideBar.vue';

export default {
  name: 'AddCustomer',
  components: {
    SideBar
  },
  data() {
    return {
      isMenuOpen: false,
      currentTime: '',
      newCustomer: {
        companyName: '',
        account: '',
        password: '',
        selectedProducts: [],
        lineAccount: '',
        contactPerson: '',
        phone: '',
        email: '',
        address: '',
        notes: ''
      },
      products: []
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
    },
    updateCustomer() {
      alert('更新功能尚未實現');
    },
    async fetchProducts() {
      try {
        const response = await fetch('http://localhost:5000/api/products', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch products');
        }

        const data = await response.json();
        this.products = data.map(product => ({
          name: product.name,
          value: product.id.toString()
        }));
      } catch (error) {
        console.error('Error fetching products:', error);
      }
    }
  },
  created() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
    document.title = '管理者系統';
    this.fetchProducts();
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
