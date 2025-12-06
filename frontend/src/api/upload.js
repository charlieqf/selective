import apiClient from './client'

export default {
    uploadImage(file) {
        const formData = new FormData()
        formData.append('file', file)

        return apiClient.post('/upload', formData)
    },

    deleteImage(public_id) {
        return apiClient.delete('/upload', {
            data: { public_id }
        })
    }
}
