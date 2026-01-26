/**
 * 計算兩點之間的距離（公里）
 * @param {number} lat1 - 起點緯度
 * @param {number} lng1 - 起點經度
 * @param {number} lat2 - 終點緯度
 * @param {number} lng2 - 終點經度
 * @returns {number} 距離（公里）
 */
export function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // 地球半徑（公里）
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = 
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

/**
 * 格式化距離顯示
 * @param {number} distance - 距離（公里）
 * @returns {string} 格式化後的距離字符串
 */
export function formatDistance(distance) {
    if (distance < 1) {
        return `${Math.round(distance * 1000)} 公尺`;
    }
    return `${distance.toFixed(1)} 公里`;
}

/**
 * 過濾餐廳標籤（移除「一般」標籤）
 * @param {Array<string>} tags - 標籤列表
 * @returns {Array<string>} 過濾後的標籤列表
 */
export function filterGeneralTags(tags) {
    return (tags || []).filter(tag => tag !== '一般');
}

/**
 * 初始化照片輪播功能
 */
export function initImageCarousels() {
    const carousels = document.querySelectorAll('.image-carousel');
    
    carousels.forEach(carousel => {
        const carouselId = carousel.getAttribute('data-carousel');
        const slides = carousel.querySelectorAll('.carousel-slide');
        const prevBtn = document.querySelector(`.carousel-prev[data-carousel="${carouselId}"]`);
        const nextBtn = document.querySelector(`.carousel-next[data-carousel="${carouselId}"]`);
        const indicators = document.querySelectorAll(`.carousel-indicators[data-carousel="${carouselId}"] .indicator`);
        
        if (slides.length === 0) return;
        
        let currentSlide = 0;
        const totalSlides = slides.length;
        
        function showSlide(index) {
            if (index < 0) {
                currentSlide = 0;
                return;
            } else if (index >= totalSlides) {
                currentSlide = totalSlides - 1;
                return;
            } else {
                currentSlide = index;
            }
            
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === currentSlide);
            });
            
            indicators.forEach((indicator, i) => {
                indicator.classList.toggle('active', i === currentSlide);
            });
            
            if (prevBtn) {
                prevBtn.style.opacity = currentSlide === 0 ? '0.5' : '1';
                prevBtn.style.pointerEvents = currentSlide === 0 ? 'none' : 'all';
            }
            if (nextBtn) {
                nextBtn.style.opacity = currentSlide === totalSlides - 1 ? '0.5' : '1';
                nextBtn.style.pointerEvents = currentSlide === totalSlides - 1 ? 'none' : 'all';
            }
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => showSlide(currentSlide - 1));
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => showSlide(currentSlide + 1));
        }
        
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => showSlide(index));
        });
        
        if (prevBtn && totalSlides > 1) {
            prevBtn.style.opacity = '0.5';
            prevBtn.style.pointerEvents = 'none';
        }
        
        // 觸摸滑動支持
        let touchStartX = 0;
        let touchEndX = 0;
        
        carousel.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        carousel.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            const diff = touchStartX - touchEndX;
            const swipeThreshold = 50;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0 && currentSlide < totalSlides - 1) {
                    showSlide(currentSlide + 1);
                } else if (diff < 0 && currentSlide > 0) {
                    showSlide(currentSlide - 1);
                }
            }
        }, { passive: true });
    });
}
