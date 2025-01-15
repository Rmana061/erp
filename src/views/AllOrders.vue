<!-- 所有訂單 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi Sales01</span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
          <h2>所有訂單 (按照日期排序)</h2>
          <button class="export-btn" @click="exportToExcel">📊 報表匯出</button>
          
          <div class="table-container">
            <table id="ordersTable">
              <thead>
                <tr>
                  <th></th>
                  <th>日期</th>
                  <th>客戶</th>
                  <th>品項</th>
                  <th>數量 kg</th>
                  <th>訂單編號</th>
                  <th>備註</th>
                  <th>核可</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(order, index) in orders" :key="index">
                  <td>{{ index + 1 }}</td>
                  <td>{{ order.date }}</td>
                  <td>{{ order.customer }}</td>
                  <td>{{ order.item }}</td>
                  <td>{{ order.quantity }}</td>
                  <td>{{ order.orderNumber }}</td>
                  <td>{{ order.notes }}</td>
                  <td><span :class="statusClass(order.status)">{{ order.statusText }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination">
            <button @click="changePage(-1)">上一頁</button>
            <span>{{ currentPage }}</span> / <span>{{ totalPages }}</span>
            <button @click="changePage(1)">下一頁</button>
          </div>
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import SideBar from '../components/SideBar.vue';

export default {
  name: 'AllOrders',
  components: {
    SideBar
  },
  data() {
    return {
      currentTime: '',
      currentPage: 1,
      totalPages: 5,
      orders: [
        { date: '08/15', customer: 'A公司', item: '漂白水', quantity: 10, orderNumber: 'T240815001', notes: '', status: 'approved', statusText: 'V' },
        { date: '08/15', customer: 'A公司', item: '硫酸', quantity: 5, orderNumber: 'T240815002', notes: '', status: 'approved', statusText: 'V' },
        { date: '08/15', customer: 'B公司', item: '鹽酸', quantity: 5, orderNumber: 'T240815003', notes: '', status: 'approved', statusText: 'V' },
        { date: '08/15', customer: 'C公司', item: '硫酸', quantity: 5, orderNumber: 'T240815004', notes: '', status: 'approved', statusText: 'V' },
        { date: '08/15', customer: 'D公司', item: '漂白水', quantity: 20, orderNumber: 'T240815005', notes: '', status: 'rejected', statusText: 'X' },
        { date: '08/14', customer: 'A公司', item: '漂白水', quantity: 15, orderNumber: 'T240814006', notes: '', status: 'approved', statusText: 'V' },
        { date: '08/13', customer: 'A公司', item: '硫酸', quantity: 5, orderNumber: 'T240813007', notes: '', status: 'approved', statusText: 'V' },
        { date: '08/12', customer: 'B公司', item: '鹽酸', quantity: 10, orderNumber: 'T240812008', notes: '', status: 'approved', statusText: 'V' },
        { date: '08/12', customer: 'C公司', item: '硫酸', quantity: 20, orderNumber: 'T240812009', notes: '', status: 'approved', statusText: 'V' },
        { date: '08/10', customer: 'D公司', item: '漂白水', quantity: 30, orderNumber: 'T240810010', notes: '', status: 'rejected', statusText: 'X' }
      ]
    };
  },
  methods: {
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
    statusClass(status) {
      switch(status) {
        case 'pending':
          return 'status status-pending';
        case 'approved':
          return 'status status-approved';
        case 'rejected':
          return 'status status-rejected';
      }
    },
    exportToExcel() {
      alert('報表匯出功能尚未實現');
    },
    changePage(direction) {
      this.currentPage += direction;
      if (this.currentPage < 1) this.currentPage = 1;
      if (this.currentPage > this.totalPages) this.currentPage = this.totalPages;
    }
  },
  mounted() {
    this.updateCurrentTime();
    this.timeInterval = setInterval(this.updateCurrentTime, 60000);
    document.title = '管理者系統';
  },
  beforeUnmount() {
    clearInterval(this.timeInterval);
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
