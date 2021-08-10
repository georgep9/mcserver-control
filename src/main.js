import Vue from 'vue'

Vue.config.productionTip = false

// import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'
// import 'bootstrap/dist/css/bootstrap.css'
// import 'bootstrap-vue/dist/bootstrap-vue.css'
// Vue.use(BootstrapVue)
// Vue.use(BootstrapVueIcons)

import App from './App.vue'

new Vue({
    render: h => h(App)
}).$mount("#app");
