// Resizable Panel Functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabsSection = document.querySelector('.tabs-section');
    const avatarSection = document.querySelector('.avatar-section');
    const resizeHandle = document.createElement('div');
    
    // Create and add resize handle
    resizeHandle.className = 'resize-handle';
    tabsSection.insertBefore(resizeHandle, tabsSection.firstChild);
    
    // Initial state - half collapsed
    let initialHeight = parseInt(getComputedStyle(tabsSection).height);
    let minHeight = 60; // Height when fully collapsed (just showing tabs)
    let maxHeight = window.innerHeight * 0.7; // Maximum height
    let startY, startHeight;
    
    // Add collapse/expand toggle functionality
    const toggleButton = document.createElement('button');
    toggleButton.className = 'panel-toggle';
    toggleButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
    tabsSection.insertBefore(toggleButton, tabsSection.firstChild);
    
    toggleButton.addEventListener('click', function() {
        if (tabsSection.classList.contains('collapsed')) {
            // Expand
            tabsSection.style.height = '50%';
            tabsSection.classList.remove('collapsed');
            this.innerHTML = '<i class="fas fa-chevron-up"></i>';
            avatarSection.style.height = '50%';
        } else {
            // Collapse
            tabsSection.style.height = minHeight + 'px';
            tabsSection.classList.add('collapsed');
            this.innerHTML = '<i class="fas fa-chevron-down"></i>';
            avatarSection.style.height = 'calc(100% - ' + minHeight + 'px)';
        }
    });
    
    // Add dragging functionality
    resizeHandle.addEventListener('mousedown', function(e) {
        startY = e.clientY;
        startHeight = parseInt(getComputedStyle(tabsSection).height);
        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);
        document.body.style.cursor = 'ns-resize';
        e.preventDefault(); // Prevent text selection
    });
    
    // Resize function
    function resize(e) {
        const deltaY = startY - e.clientY;
        const newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight + deltaY));
        
        // Update panel heights
        tabsSection.style.height = newHeight + 'px';
        avatarSection.style.height = 'calc(100% - ' + newHeight + 'px)';
        
        // Update toggle button state
        if (newHeight <= minHeight + 10) {
            tabsSection.classList.add('collapsed');
            toggleButton.innerHTML = '<i class="fas fa-chevron-down"></i>';
        } else {
            tabsSection.classList.remove('collapsed');
            toggleButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
        }
    }
    
    // Stop resize function
    function stopResize() {
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
        document.body.style.cursor = '';
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        maxHeight = window.innerHeight * 0.7;
        const currentHeight = parseInt(getComputedStyle(tabsSection).height);
        if (currentHeight > maxHeight) {
            tabsSection.style.height = maxHeight + 'px';
            avatarSection.style.height = 'calc(100% - ' + maxHeight + 'px)';
        }
    });
    
    // Add touch support for mobile devices
    resizeHandle.addEventListener('touchstart', function(e) {
        startY = e.touches[0].clientY;
        startHeight = parseInt(getComputedStyle(tabsSection).height);
        document.addEventListener('touchmove', touchResize);
        document.addEventListener('touchend', stopTouchResize);
        e.preventDefault();
    });
    
    function touchResize(e) {
        const deltaY = startY - e.touches[0].clientY;
        const newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight + deltaY));
        tabsSection.style.height = newHeight + 'px';
        avatarSection.style.height = 'calc(100% - ' + newHeight + 'px)';
        
        if (newHeight <= minHeight + 10) {
            tabsSection.classList.add('collapsed');
            toggleButton.innerHTML = '<i class="fas fa-chevron-down"></i>';
        } else {
            tabsSection.classList.remove('collapsed');
            toggleButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
        }
    }
    
    function stopTouchResize() {
        document.removeEventListener('touchmove', touchResize);
        document.removeEventListener('touchend', stopTouchResize);
    }
});
