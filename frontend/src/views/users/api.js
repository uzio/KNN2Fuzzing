import request from '@/utils/request'

export const getUsers = (page, pageSize = 10) => {
  return request.get('/login/users', { params: { page, pageSize } })
}

// 创建用户
export const createUser = (token, form) => {
  return request.put(`/login/register`, { data: form, token })
}

// 删除用户
export const deleteUser = (token, username) => {
  return request.post(`/login/users`, { token, username })
}