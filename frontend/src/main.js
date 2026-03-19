import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'

import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'
import Message from 'primevue/message'
import PToast from 'primevue/toast'
import ToastService from 'primevue/toastservice'


import 'primeicons/primeicons.css'
import './styles.css'

const app = createApp(App)

app.use(router)
app.use(ToastService)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: 'none',
    }
  },
})

app.component('PButton', Button)
app.component('PCard', Card)
app.component('PInputText', InputText)
app.component('PPassword', Password)
app.component('PTextarea', Textarea)
app.component('PSelect', Select)
app.component('PDataTable', DataTable)
app.component('PColumn', Column)
app.component('PTag', Tag)
app.component('PDivider', Divider)
app.component('PMessage', Message)
app.component('PToast', PToast)


app.mount('#app')