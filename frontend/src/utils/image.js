import { Cloudinary } from '@cloudinary/url-gen'
import { byAngle } from '@cloudinary/url-gen/actions/rotate'

const cld = new Cloudinary({
    cloud: {
        cloudName: import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
    }
})

// Safely appends buster without stripping existing signed/required query params
export function getDisplayUrl(image, updatedAt) {
    const imgObj = typeof image === 'string' ? { url: image } : image
    if (!imgObj?.url) return ''

    if (!updatedAt) return imgObj.url

    const buster = `t=${new Date(updatedAt).getTime()}`
    const separator = imgObj.url.includes('?') ? '&' : '?'
    return `${imgObj.url}${separator}${buster}`
}

// Get the Cloudinary rotated URL for full-screen/processed view
export function getRotatedUrl(image, updatedAt) {
    const imgObj = typeof image === 'string' ? { url: image, rotation: 0 } : image
    if (!imgObj?.url) return ''

    const rotation = Number(imgObj.rotation) || 0
    const hasPublicId = !!imgObj.public_id

    // If no rotation OR no public_id, return display URL (base + buster)
    if (rotation === 0 || !hasPublicId) {
        return getDisplayUrl(imgObj, updatedAt)
    }

    try {
        const myImage = cld.image(imgObj.public_id)
        myImage.rotate(byAngle(rotation))

        // Add same cache buster as display URL for consistency
        const url = myImage.toURL()
        const buster = updatedAt ? `t=${new Date(updatedAt).getTime()}` : ''
        const separator = url.includes('?') ? '&' : '?'
        return `${url}${buster ? separator + buster : ''}`
    } catch (e) {
        console.error('Cloudinary rotation failed:', e)
        return getDisplayUrl(imgObj, updatedAt)
    }
}

export function getImageStyle(image) {
    const imgObj = typeof image === 'string' ? { rotation: 0 } : image
    const rotation = Number(imgObj?.rotation) || 0
    return {
        transform: `rotate(${rotation}deg)`,
        transition: 'transform 0.3s ease'
    }
}
