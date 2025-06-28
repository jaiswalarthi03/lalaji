// Utility functions for InventoryMaster

// Generic chart rendering
function renderChart(type, ctx, data, options = {}) {
    if (window.Chart && ctx) {
        return new Chart(ctx, {
            type,
            data,
            options
        });
    }
    return null;
}

// Update or create chart by ID
function updateChart(chartId, data, options = {}) {
    const ctx = document.getElementById(chartId)?.getContext('2d');
    if (!ctx) return;
    if (window[chartId + '_instance']) {
        window[chartId + '_instance'].data = data;
        window[chartId + '_instance'].options = options;
        window[chartId + '_instance'].update();
    } else {
        window[chartId + '_instance'] = renderChart('bar', ctx, data, options);
    }
}

// Centralized error display for charts
function showChartError(chartId, message) {
    const container = document.getElementById(chartId)?.parentNode;
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
            </div>
        `;
    }
}

// Centralized fetch with error handling
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || 'Network error');
        }
        return await response.json();
    } catch (err) {
        console.error('Fetch error:', err);
        throw err;
    }
}

// Table row update utility
function updateTableRow(row, updateFn) {
    if (!row) return;
    updateFn(row);
}

// Export for module usage if needed
if (typeof module !== 'undefined') {
    module.exports = {
        renderChart,
        updateChart,
        showChartError,
        fetchData,
        updateTableRow
    };
} 