import { getVuls } from '@/views/vuls/api'
const vul = {
  state: {
    total: 0,
    vuls: [], // 漏洞列表中的漏洞,
    page: 1,
    pageSize: 10,
  },
  mutations: {
    SET_VULS (state, data) {
      state.vuls = data.vuls;
      console.log(state.vuls);
      state.total = data.count;
    },
    SET_VULS_PAGINATION (state, {page, pageSize}) {
      state.page = page;
      state.pageSize = pageSize? pageSize: 10;
    }
  },
  actions: {
    reloadVuls (context) {
      return getVuls(context.state.page, context.state.pageSize).then(response => {
        if (response.code >= 500) {
          throw new Error('服务器连接失败')
        }
        context.commit('SET_VULS', response.data)
        return response.data
      })
    }
  },
}

export default vul
