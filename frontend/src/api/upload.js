import apiClient from './client'

function resolveFilename(file) {
    // Preserve original name when available and has an extension
    if (file?.name && file.name.includes('.')) {
        return file.name
    }
    // Fallback based on MIME type to satisfy backend extension check
    const mimeToExt = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/webp': '.webp'
    }
    const ext = mimeToExt[file?.type] || '.jpg'
    return `upload${ext}`
}

export default {
    uploadImage(file) {
        const formData = new FormData()
        formData.append('file', file, resolveFilename(file))

        return apiClient.post('/upload', formData)
    },

    deleteImage(public_id) {
        return apiClient.delete('/upload', {
            data: { public_id }
        })
    }
}
