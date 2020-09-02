import Vue from 'vue'
import App from './App.vue'
import FunctionalCalendar from 'vue-functional-calendar';

Vue.use(FunctionalCalendar, {
    dayNames: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
});

// Vue.use(VueGoogleCharts)
Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
