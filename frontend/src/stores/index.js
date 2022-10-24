import Vuex from 'vuex'
import Vue from 'vue'
import workstation from './workstation'
import fuzz from './fuzz'
import user from './user'
import vul from './vul'

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    workstation,
    fuzz,
    user,
    vul
  }
})

export default store
