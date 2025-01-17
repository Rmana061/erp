<!-- 今日訂單 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,</span>
        <span>{{ currentTime }}</span>
      </div>
      
      <div class="content-wrapper">
        <div class="page-header">
          <h2>今日訂單</h2>
          <button class="export-btn" @click="exportOrders">
            <i class="fas fa-file-export"></i> 報表匯出
          </button>
        </div>

        <div class="scrollable-content">
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>序號</th>
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
                  <td>{{ order.note }}</td>
                  <td>
                    <div class="status-buttons">
                      <button 
                        class="approve-btn" 
                        @click="approveOrder(order.id)"
                        :disabled="order.status === 'approved'">
                        核准
                      </button>
                      <button 
                        class="reject-btn" 
                        @click="rejectOrder(order.id)"
                        :disabled="order.status === 'rejected'">
                        駁回
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <div class="notification">
          結果會透過LINE發送
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import { timeMixin } from '../mixins/timeMixin';
import { adminMixin } from '../mixins/adminMixin';
import SideBar from '../components/SideBar.vue';
import axios from 'axios';

export default {
  name: 'TodayOrders',
  components: {
    SideBar
  },
  mixins: [timeMixin, adminMixin],
  data() {
    return {
      orders: [
        {
          id: 1,
          date: '08/15',
          customer: 'A公司',
          item: '漂白水',
          quantity: '10',
          orderNumber: 'T240815001',
          note: '',
          status: 'pending'
        },
        {
          id: 2,
          date: '08/15',
          customer: 'A公司',
          item: '硫酸',
          quantity: '5',
          orderNumber: 'T240815002',
          note: '',
          status: 'pending'
        },
        {
          id: 3,
          date: '08/15',
          customer: 'B公司',
          item: '鹽酸',
          quantity: '5',
          orderNumber: 'T240815003',
          note: '',
          status: 'pending'
        },
        {
          id: 4,
          date: '08/15',
          customer: 'C公司',
          item: '硫酸',
          quantity: '5',
          orderNumber: 'T240815004',
          note: '',
          status: 'pending'
        },
        {
          id: 5,
          date: '08/15',
          customer: 'D公司',
          item: '漂白水',
          quantity: '20',
          orderNumber: 'T240815005',
          note: '',
          status: 'pending'
        }
      ]
    };
  },
  methods: {
    exportOrders() {
      alert('匯出功能尚未實現');
    },
    approveOrder(orderId) {
      const order = this.orders.find(o => o.id === orderId);
      if (order) {
        order.status = 'approved';
      }
    },
    rejectOrder(orderId) {
      const order = this.orders.find(o => o.id === orderId);
      if (order) {
        order.status = 'rejected';
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>

