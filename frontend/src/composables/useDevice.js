import { useMediaQuery } from '@vueuse/core'

/**
 * 响应式设备检测
 * 用于在组件中根据设备类型调整布局
 */
export function useDevice() {
    const isMobile = useMediaQuery('(max-width: 768px)')
    const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)')
    const isDesktop = useMediaQuery('(min-width: 1025px)')
    const isLargeDesktop = useMediaQuery('(min-width: 1920px)')

    return {
        isMobile,
        isTablet,
        isDesktop,
        isLargeDesktop
    }
}
