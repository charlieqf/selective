

// Safely appends buster without stripping existing signed/required query params
export function getDisplayUrl(image, updatedAt) {
    const imgObj = typeof image === 'string' ? { url: image } : image
    if (!imgObj?.url) return ''

    if (!updatedAt) return imgObj.url

    const buster = `t=${new Date(updatedAt).getTime()}`
    const separator = imgObj.url.includes('?') ? '&' : '?'
    return `${imgObj.url}${separator}${buster}`
}


export function getImageStyle(image) {
    const imgObj = typeof image === 'string' ? { rotation: 0 } : image
    const rotation = Number(imgObj?.rotation) || 0
    return {
        transform: `rotate(${rotation}deg)`,
        transition: 'transform 0.3s ease'
    }
}
