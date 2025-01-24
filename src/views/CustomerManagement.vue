<!-- 客戶管理 -->
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
        <div class="scrollable-content">
          <h2>客戶管理</h2>
          <div class="action-buttons">
            <router-link to="/add-customer">
              <button class="action-button">+ 新增客戶</button>
            </router-link>
            <button class="action-button" @click="exportCustomers">📊 資料匯出</button>
            <input type="text" v-model="searchQuery" placeholder="搜尋客戶..." class="search-input">
          </div>

          <div class="table-container">
            <table id="customersTable">
              <thead>
                <tr>
                  <th>公司名稱</th>
                  <th>聯絡人</th>
                  <th>電話</th>
                  <th>Email</th>
                  <th>地址</th>
                  <th>建立時間</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(customer, index) in filteredCustomers" :key="customer.id">
                  <td>{{ customer.company_name }}</td>
                  <td>{{ customer.contact_person }}</td>
                  <td>{{ customer.phone }}</td>
                  <td>{{ customer.email }}</td>
                  <td>{{ customer.address }}</td>
                  <td>{{ customer.created_at }}</td>
                  <td>
                    <router-link :to="{ 
                      path: '/add-customer', 
                      query: { 
                        mode: 'edit',
                        id: customer.id,
                        company_name: customer.company_name,
                        username: customer.username,
                        contact_person: customer.contact_person,
                        phone: customer.phone,
                        email: customer.email,
                        address: customer.address,
                        line_account: customer.line_account || '',
                        viewable_products: customer.viewable_products || '',
                        remark: customer.remark || ''
                      }
                    }">
                      <button class="table-button edit">編輯</button>
                    </router-link>
                    <button class="table-button delete" @click="deleteCustomerRow(customer.id)">刪除</button>
                  </td>
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
import axios from 'axios';
import * as XLSX from 'xlsx';
import SideBar from '../components/SideBar.vue';
import { adminMixin } from '../mixins/adminMixin';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'CustomerManagement',
  mixins: [adminMixin],
  components: {
    SideBar
  },
  data() {
    return {
      currentTime: '',
      isMenuOpen: false,
      customers: [],
      searchQuery: ''
    };
  },
  computed: {
    filteredCustomers() {
      return this.customers.filter(customer => {
        const searchLower = this.searchQuery.toLowerCase();
        return (customer.company_name || '').toLowerCase().includes(searchLower) || 
               (customer.contact_person || '').toLowerCase().includes(searchLower) || 
               (customer.phone || '').toLowerCase().includes(searchLower) || 
               (customer.email || '').toLowerCase().includes(searchLower) || 
               (customer.address || '').toLowerCase().includes(searchLower);
      });
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
    async fetchCustomers() {
      try {
        const response = await axios.post(getApiUrl(API_PATHS.CUSTOMER_LIST), {}, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        if (response.data && response.data.status === 'success') {
          this.customers = response.data.data.map(customer => ({
            ...customer,
            viewable_products: customer.viewable_products || '',
            line_account: customer.line_account || '',
            remark: customer.remark || ''
          }));
          console.log('Fetched customers:', this.customers);
        } else {
          console.error('獲取客戶數據失敗:', response.data.message);
        }
      } catch (error) {
        console.error('Error fetching customer data:', error);
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        }
      }
    },
    async deleteCustomerRow(customerId) {
      if (!confirm('確定要刪除此客戶嗎？')) return;

      try {
        const response = await axios.post(
          getApiUrl(API_PATHS.DELETE_CUSTOMER),
          { id: customerId },
          {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          alert('客戶刪除成功');
          this.fetchCustomers();  // 重新获取客户列表
        } else {
          throw new Error(response.data.message || '刪除客戶失敗');
        }
      } catch (error) {
        console.error('Error deleting customer:', error);
        alert('刪除客戶失敗：' + (error.response?.data?.message || error.message));
      }
    },
    exportCustomers() {
      const headers = [
        '客戶編號',
        '公司名稱',
        '帳號',
        '聯絡人',
        '電話',
        'Email',
        '地址',
        '建立時間',
        '更新時間'
      ];
      
      const data = [
        headers,
        ...this.customers.map(customer => [
          customer.id,
          customer.company_name,
          customer.username,
          customer.contact_person,
          customer.phone,
          customer.email,
          customer.address,
          customer.created_at,
          customer.updated_at
        ])
      ];

      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet(data);
      
      const wscols = [
        { wch: 10 },
        { wch: 25 },
        { wch: 15 },
        { wch: 15 },
        { wch: 15 },
        { wch: 25 },
        { wch: 40 },
        { wch: 20 },
        { wch: 20 }
      ];
      ws['!cols'] = wscols;

      XLSX.utils.book_append_sheet(wb, ws, '客戶清單');
      XLSX.writeFile(wb, '客戶資料.xlsx');
    }
  },
  mounted() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
    document.title = '管理者系統';
    this.fetchCustomers();
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
