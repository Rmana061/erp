<!-- 客戶首頁 -->
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
          <h2>首頁</h2>
          <p>以下為過去兩週的訂貨紀錄</p>
        </div>

        <div class="scrollable-content">
          <table class="order-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>品項</th>
                <th>數量 kg</th>
                <th>狀態</th>
                <th>訂單編號</th>
                <th>備註</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(order, index) in orders" :key="index">
                <td>{{ order.date }}</td>
                <td>{{ order.item }}</td>
                <td>{{ order.quantity }}</td>
                <td :class="statusClass(order.status)">{{ order.statusText }}</td>
                <td>{{ order.orderNumber }}</td>
                <td>{{ order.notes }}</td>
              </tr>
            </tbody>
          </table>
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
  name: 'CustomerHomepage',
  components: {
    SideBar
  },
  mixins: [timeMixin, companyMixin],
  mounted() {
    document.title = '客戶系統';
  },
  data() {
    return {
      orders: [
        { date: '08/15', item: '漂白水', quantity: 10, status: 'rejected', statusText: 'X', orderNumber: 'T240815001', notes: '' },
        { date: '08/15', item: '硫酸', quantity: 5, status: 'processing', statusText: '審核中', orderNumber: 'T240815002', notes: '' },
        { date: '08/15', item: '鹽酸', quantity: 5, status: 'approved', statusText: 'V', orderNumber: 'T240815003', notes: '' },
        { date: '08/15', item: '硝酸', quantity: 5, status: 'approved', statusText: 'V', orderNumber: 'T240815004', notes: '' },
        { date: '08/10', item: '漂白水', quantity: 20, status: 'approved', statusText: 'V', orderNumber: 'T240815005', notes: '' }
      ]
    };
  },
  methods: {
    statusClass(status) {
      switch (status) {
        case 'rejected':
          return 'status-rejected';
        case 'approved':
          return 'status-approved';
        case 'processing':
          return 'status-processing';
        default:
          return '';
      }
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
