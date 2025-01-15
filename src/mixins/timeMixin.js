export const timeMixin = {
  data() {
    return {
      currentTime: ''
    }
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
    }
  },
  created() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
  }
} 