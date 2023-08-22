import { createApp } from 'vue'
import App from './App.vue'

import './assets/main.css'
// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import router from './router' 

const vuetify = createVuetify({
  components,
  directives,
})

createApp(App).use(vuetify).use(router).mount('#app')
