<!-- 訂貨系統 -->
<template>
  <body class="customer-mode">
  <div class="container">
    <SideBar menu-type="customer" />
    
    <div class="main-content">
      <div class="header">
        <span>Hi {{ companyName }}您好,</span>
        <span id="current-time">{{ currentTime }}</span>
      </div>
      
      <div class="content-wrapper">
        <div class="page-header">
          <h2>訂貨系統</h2>
        </div>

        <div class="action-buttons">
          <button class="action-button" @click="navigateToAddOrder">+ 新增訂單</button>
          <button class="action-button" @click="cancelOrder">- 取消訂單</button>
        </div>

        <div class="scrollable-content">
          <div class="table-container">
          <table class="order-table">
            <thead>
              <tr>
                <th>訂單編號</th>
                <th>日期</th>
                <th>品項</th>
                <th>數量/規格</th>
                <th>單位</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(order, index) in orders" :key="index">
                <td>{{ order.id }}</td>
                <td>{{ order.date }}</td>
                <td>{{ order.item }}</td>
                <td>{{ order.quantity }}</td>
                <td>{{ order.unit }}</td>
                <td>{{ order.status }}</td>
              </tr>
            </tbody>
          </table>
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

export default {
  name: 'OrderSystem',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  data() {
    return {
      orders: [
        { id: 'T240815001', date: '2024/08/15', item: '漂白水', quantity: ' 10KG', unit: '', status: '審核中' },
        { id: '', date: '', item: '', quantity: '', unit: '', status: '' },
        { id: '', date: '', item: '', quantity: '', unit: '', status: '' }
      ]
    };
  },
  methods: {
    navigateToAddOrder() {
      this.$router.push('/add-order-plan-b');
    },
    cancelOrder() {
      alert('取消訂單功能尚未實現');
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