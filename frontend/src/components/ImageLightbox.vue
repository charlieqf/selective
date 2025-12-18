<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { NButton, NIcon } from 'naive-ui'
import { Close, RemoveCircleOutline, AddCircleOutline } from '@vicons/ionicons5'

const props = defineProps({
  images: {
    type: Array,
    required: true
  },
  initialIndex: {
    type: Number,
    default: 0
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const currentIndex = ref(props.initialIndex)
const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const lastTouch = ref({ x: 0, y: 0 })
const lastPinchDistance = ref(0)
const imageRef = ref(null)

// Constants
const MIN_SCALE = 1
const MAX_SCALE = 4
const DOUBLE_TAP_THRESHOLD = 300

// For double-tap detection
let lastTapTime = 0

// Current image
const currentImage = computed(() => props.images[currentIndex.value])

// Transform style
const imageStyle = computed(() => ({
  transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value})`,
  transition: isDragging.value ? 'none' : 'transform 0.2s ease-out'
}))

// Watch for index changes from parent
watch(() => props.initialIndex, (newIndex) => {
  currentIndex.value = newIndex
  resetTransform()
})

// Watch show prop to reset when lightbox opens
watch(() => props.show, (isShown) => {
  if (isShown) {
    currentIndex.value = props.initialIndex
    resetTransform()
    // Prevent body scroll when lightbox is open
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

function resetTransform() {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
}

function close() {
  emit('close')
}

function prevImage() {
  if (currentIndex.value > 0) {
    currentIndex.value--
    resetTransform()
  }
}

function nextImage() {
  if (currentIndex.value < props.images.length - 1) {
    currentIndex.value++
    resetTransform()
  }
}

// Zoom controls
function zoomIn() {
  const newScale = Math.min(scale.value + 0.5, MAX_SCALE)
  scale.value = newScale
}

function zoomOut() {
  const newScale = Math.max(scale.value - 0.5, MIN_SCALE)
  if (newScale === MIN_SCALE) {
    resetTransform()
  } else {
    scale.value = newScale
  }
}

// Handle keyboard events
function handleKeydown(e) {
  if (!props.show) return
  
  switch (e.key) {
    case 'Escape':
      close()
      break
    case 'ArrowLeft':
      prevImage()
      break
    case 'ArrowRight':
      nextImage()
      break
    case '+':
    case '=':
      zoomIn()
      break
    case '-':
      zoomOut()
      break
  }
}

// Touch handlers for pinch-zoom and pan
function handleTouchStart(e) {
  if (e.touches.length === 2) {
    // Pinch start
    lastPinchDistance.value = getDistance(e.touches[0], e.touches[1])
  } else if (e.touches.length === 1) {
    // Check for double-tap
    const now = Date.now()
    if (now - lastTapTime < DOUBLE_TAP_THRESHOLD) {
      handleDoubleTap(e.touches[0])
      e.preventDefault()
    }
    lastTapTime = now
    
    // Pan start
    if (scale.value > 1) {
      isDragging.value = true
      dragStart.value = { x: e.touches[0].clientX, y: e.touches[0].clientY }
      lastTouch.value = { x: translateX.value, y: translateY.value }
    }
  }
}

function handleTouchMove(e) {
  if (e.touches.length === 2) {
    // Pinch zoom
    e.preventDefault()
    const distance = getDistance(e.touches[0], e.touches[1])
    const scaleDelta = distance / lastPinchDistance.value
    const newScale = Math.min(Math.max(scale.value * scaleDelta, MIN_SCALE), MAX_SCALE)
    scale.value = newScale
    lastPinchDistance.value = distance
    
    // Reset position if zooming out to min scale
    if (newScale === MIN_SCALE) {
      translateX.value = 0
      translateY.value = 0
    }
  } else if (e.touches.length === 1 && isDragging.value) {
    // Pan
    e.preventDefault()
    const deltaX = e.touches[0].clientX - dragStart.value.x
    const deltaY = e.touches[0].clientY - dragStart.value.y
    translateX.value = lastTouch.value.x + deltaX
    translateY.value = lastTouch.value.y + deltaY
  }
}

function handleTouchEnd() {
  isDragging.value = false
  constrainPosition()
}

function handleDoubleTap(touch) {
  if (scale.value > MIN_SCALE) {
    // Zoom out
    resetTransform()
  } else {
    // Zoom in to 2x at the tap location
    scale.value = 2
    
    // Calculate the offset to zoom toward the tap point
    if (imageRef.value) {
      const rect = imageRef.value.getBoundingClientRect()
      const offsetX = touch.clientX - rect.left - rect.width / 2
      const offsetY = touch.clientY - rect.top - rect.height / 2
      translateX.value = -offsetX
      translateY.value = -offsetY
    }
  }
}

function getDistance(touch1, touch2) {
  return Math.sqrt(
    Math.pow(touch2.clientX - touch1.clientX, 2) +
    Math.pow(touch2.clientY - touch1.clientY, 2)
  )
}

function constrainPosition() {
  // Limit the pan area when zoomed in
  if (scale.value <= MIN_SCALE) {
    translateX.value = 0
    translateY.value = 0
  }
}

// Mouse wheel zoom (for desktop)
function handleWheel(e) {
  if (!props.show) return
  e.preventDefault()
  
  if (e.deltaY < 0) {
    zoomIn()
  } else {
    zoomOut()
  }
}

// Handle backdrop click
function handleBackdropClick(e) {
  if (e.target === e.currentTarget) {
    close()
  }
}

// Swipe detection for navigation
let touchStartX = 0
let touchStartY = 0
const SWIPE_THRESHOLD = 50

function handleSwipeStart(e) {
  if (e.touches.length === 1 && scale.value === 1) {
    touchStartX = e.touches[0].clientX
    touchStartY = e.touches[0].clientY
  }
}

function handleSwipeEnd(e) {
  if (scale.value !== 1) return
  
  const touchEndX = e.changedTouches[0].clientX
  const touchEndY = e.changedTouches[0].clientY
  const deltaX = touchEndX - touchStartX
  const deltaY = touchEndY - touchStartY
  
  // Only horizontal swipes that are more horizontal than vertical
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > SWIPE_THRESHOLD) {
    if (deltaX > 0) {
      prevImage()
    } else {
      nextImage()
    }
  }
}

// Mount/unmount lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="lightbox-overlay"
      @click="handleBackdropClick"
      @wheel.prevent="handleWheel"
    >
      <!-- Close button -->
      <n-button
        circle
        class="close-btn"
        @click="close"
        aria-label="Close"
      >
        <template #icon>
          <n-icon size="24"><Close /></n-icon>
        </template>
      </n-button>

      <!-- Zoom controls (visible on larger screens) -->
      <div class="zoom-controls">
        <n-button circle secondary @click="zoomOut" :disabled="scale <= MIN_SCALE" aria-label="Zoom out">
          <template #icon>
            <n-icon><RemoveCircleOutline /></n-icon>
          </template>
        </n-button>
        <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
        <n-button circle secondary @click="zoomIn" :disabled="scale >= MAX_SCALE" aria-label="Zoom in">
          <template #icon>
            <n-icon><AddCircleOutline /></n-icon>
          </template>
        </n-button>
      </div>

      <!-- Image counter -->
      <div class="image-counter" v-if="images.length > 1">
        {{ currentIndex + 1 }} / {{ images.length }}
      </div>

      <!-- Navigation arrows for multi-image (desktop) -->
      <button
        v-if="images.length > 1 && currentIndex > 0"
        class="nav-arrow nav-arrow-left"
        @click.stop="prevImage"
        aria-label="Previous image"
      >
        ‹
      </button>
      <button
        v-if="images.length > 1 && currentIndex < images.length - 1"
        class="nav-arrow nav-arrow-right"
        @click.stop="nextImage"
        aria-label="Next image"
      >
        ›
      </button>

      <!-- Image container -->
      <div
        class="image-container"
        @touchstart="handleTouchStart"
        @touchstart.passive="handleSwipeStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
        @touchend.passive="handleSwipeEnd"
      >
        <img
          ref="imageRef"
          :src="currentImage"
          :style="imageStyle"
          class="lightbox-image"
          alt="Full screen image"
          draggable="false"
          @click.stop
        />
      </div>

      <!-- Mobile hint -->
      <div class="mobile-hint">
        Double-tap to zoom • Swipe to navigate
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.95);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: none;
}

.close-btn {
  position: absolute;
  top: env(safe-area-inset-top, 16px);
  right: 16px;
  z-index: 10001;
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  margin-top: 16px;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.3) !important;
}

.zoom-controls {
  position: absolute;
  bottom: calc(env(safe-area-inset-bottom, 16px) + 60px);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: rgba(0, 0, 0, 0.6);
  padding: 8px 16px;
  border-radius: 24px;
  z-index: 10001;
}

.zoom-controls :deep(.n-button) {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

.zoom-level {
  color: white;
  font-size: 14px;
  min-width: 50px;
  text-align: center;
}

.image-counter {
  position: absolute;
  top: env(safe-area-inset-top, 16px);
  left: 50%;
  transform: translateX(-50%);
  color: white;
  font-size: 14px;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 6px 16px;
  border-radius: 16px;
  margin-top: 16px;
  z-index: 10001;
}

.nav-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  font-size: 32px;
  cursor: pointer;
  z-index: 10001;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.nav-arrow:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.nav-arrow-left {
  left: 16px;
}

.nav-arrow-right {
  right: 16px;
}

/* Hide navigation arrows on mobile */
@media (max-width: 768px) {
  .nav-arrow {
    display: none;
  }
  
  .zoom-controls {
    bottom: calc(env(safe-area-inset-bottom, 16px) + 40px);
  }
}

.image-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.lightbox-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  user-select: none;
  -webkit-user-drag: none;
  will-change: transform;
}

.mobile-hint {
  position: absolute;
  bottom: calc(env(safe-area-inset-bottom, 8px) + 8px);
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  text-align: center;
  z-index: 10001;
}

/* Hide hint on desktop */
@media (min-width: 769px) {
  .mobile-hint {
    display: none;
  }
}
</style>
