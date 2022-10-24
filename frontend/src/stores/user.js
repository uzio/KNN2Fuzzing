import { getToken, setToken, removeToken } from '@/utils/auth'
import { login, getInfo } from '@/views/login/api'
import { getUsers } from "@/views/users/api";

const user = {
  state: {
    users: [], // 用户管理页面的表格中展示的用户数组
    token: getToken(),
    name: '',
    info: {},
    createDialog: false, // 新建任务窗口
    page: 1,
    pageSize: 10
  },

  mutations: {
    SET_TOKEN: (state, token) => {
      state.token = token
    },
    SET_NAME: (state, name) => {
      state.name = name
    },
    SET_INFO: (state, info) => {
      state.info = info
    },
    CHANGE_USER_CREA_DIALOG(state, status) {
      state.createDialog = status
    },
    SET_USERS: (state, users) => {
      state.users = users
    },
  },

  actions: {
    GetUsers({ commit, state }) {
      getUsers(state.page, state.pageSize).then(resp => {
        commit('SET_USERS', resp.data.users);
      })
    },
    // 登录
    Login({ commit }, userForm) {
      const username = userForm.username.trim()
      const password = userForm.password.trim()

      return login(username, password).then(response => {
        const data = response.data
        setToken(data.token)
        commit('SET_INFO', data.info)
        commit('SET_NAME', data.username)
        commit('SET_TOKEN', data.token)
      })
    },

    // 获取用户信息
    GetInfo({ commit, state }) {
      return new Promise((resolve, reject) => {
        getInfo(state.token).then(response => {
          const data = response.data
          commit('SET_INFO', data.info)
          commit('SET_NAME', data.username)
          resolve(response)
        }).catch(error => {
          reject(error)
        })
      })
    },

    // 登出
    LogOut({ commit, state }) {
      return new Promise((resolve, reject) => {
        commit('SET_TOKEN', '')
        removeToken()
        resolve()
      })
    }
  }
}

export default user
