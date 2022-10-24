import request from '@/utils/request'

export const getCases = (page, pageSize = 10) => {
  return request.get('/cases', { params: { page, pageSize } })
}

export const deleteCase = (id) => {
  return request.delete('/cases', { data: id })
}

// 上传测试用例文件
export const uploadFile = (formData) => {
  return request.post('/cases', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
