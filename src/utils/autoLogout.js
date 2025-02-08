export const AUTO_LOGOUT_TIME = 30 * 60 * 1000; // 30分鐘
export const IS_AUTO_LOGOUT_ENABLED = import.meta.env.VITE_APP_ENABLE_AUTO_LOGOUT !== 'false';

export function setupAutoLogout(router) {
    try {
        if (!IS_AUTO_LOGOUT_ENABLED) return;

        let logoutTimer;

        function resetTimer() {
            if (logoutTimer) clearTimeout(logoutTimer);
            
            const isCustomer = localStorage.getItem('customer_id');
            const isAdmin = localStorage.getItem('admin_id');
            
            if (isCustomer || isAdmin) {
                logoutTimer = setTimeout(async () => {
                    try {
                        const loginPath = isAdmin ? '/admin-login' : '/customer-login';
                        localStorage.clear();
                        sessionStorage.clear();
                        await router.push(loginPath);
                        alert('由於長時間未操作，系統已自動登出');
                    } catch (error) {
                        console.error('自動登出失敗:', error);
                    }
                }, AUTO_LOGOUT_TIME);
            }
        }

        const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
        events.forEach(event => {
            document.addEventListener(event, resetTimer);
        });

        resetTimer();

        return () => {
            if (logoutTimer) clearTimeout(logoutTimer);
            events.forEach(event => {
                document.removeEventListener(event, resetTimer);
            });
        };
    } catch (error) {
        console.error('設置自動登出失敗:', error);
        return () => {}; // 返回空函數避免錯誤
    }
}
