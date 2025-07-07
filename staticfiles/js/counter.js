// Animated counter function
function animateCounter(element, target, duration = 2000, decimals = 0) {
    let start = 0;
    const end = parseFloat(target);
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const value = progress * (end - start) + start;
        element.textContent = value.toFixed(decimals);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Initialize counters when they come into view
document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const target = element.getAttribute('data-target');
                const decimals = target.includes('.') ? 1 : 0;
                animateCounter(element, target, 2000, decimals);
                observer.unobserve(element);
            }
        });
    }, {
        threshold: 0.5
    });

    document.querySelectorAll('.stat-number').forEach(counter => {
        observer.observe(counter);
    });
});
