// Reports page functionality
// Import utilities
// <script src="/static/js/utils.js"></script> should be included in HTML

// Use utility functions from utils.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize default chart
    const currentPeriod = 'weekly'; // Default to weekly view
    initializeReports(currentPeriod);
    
    // Set up event listeners for report type selection
    const reportTypeSelect = document.getElementById('reportTypeSelect');
    if (reportTypeSelect) {
        reportTypeSelect.addEventListener('change', function() {
            const period = document.querySelector('.time-filter.btn-primary').dataset.period || 'weekly';
            updateReportType(this.value, period);
        });
    }
    
    // Set up event listeners for time period filters
    const timeFilters = document.querySelectorAll('.time-filter');
    timeFilters.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            timeFilters.forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
            });
            this.classList.remove('btn-outline-primary');
            this.classList.add('btn-primary');
            
            // Update charts for the selected period
            const period = this.dataset.period;
            const reportType = document.getElementById('reportTypeSelect').value;
            updateReportType(reportType, period);
        });
    });

    // Ensure Start Call button works in reports screen
    const startCallButton = document.getElementById('startCallButton');
    if (startCallButton && window.startCall) {
        startCallButton.addEventListener('click', window.startCall);
    }

    // Initialize navigation
    initializeNavigation();
    
    // Load initial data
    loadPricingOptimizationData();

    // Subscribe to simulation events from inventory.js
    window.addEventListener('simulation-complete', handleSimulationData);
});

// Initialize reports
function initializeReports(period) {
    const reportType = document.getElementById('reportTypeSelect').value;
    updateReportType(reportType, period);
}

// Update the report based on type and period
function updateReportType(reportType, period) {
    // Update title
    document.getElementById('reportSummaryTitle').textContent = 
        document.querySelector(`#reportTypeSelect option[value="${reportType}"]`).textContent;
    
    // Clear existing charts
    destroyCharts();
    
    // Show loading state
    const mainChartContainer = document.getElementById('mainChart').parentNode;
    mainChartContainer.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">Loading chart data...</p></div>';
    
    // Add back canvas elements
    setTimeout(() => {
        mainChartContainer.innerHTML = '<canvas id="mainChart"></canvas>';
        document.getElementById('secondaryChart').parentNode.innerHTML = '<canvas id="secondaryChart"></canvas>';
        document.getElementById('tertiaryChart').parentNode.innerHTML = '<canvas id="tertiaryChart"></canvas>';
        
        // Fetch data and create charts
        fetchReportData(reportType, period);
    }, 500);
}

// Destroy existing charts to prevent memory leaks
function destroyCharts() {
    Chart.getChart('mainChart')?.destroy();
    Chart.getChart('secondaryChart')?.destroy();
    Chart.getChart('tertiaryChart')?.destroy();
}

// Fetch report data from API
function fetchReportData(reportType, period) {
    fetch(`/api/reports/${reportType}?period=${period}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                renderCharts(reportType, period, data.data);
                updateReportStats(data.stats);
            } else {
                showErrorState('Failed to load report data');
            }
        })
        .catch(error => {
            console.error('Error fetching report data:', error);
            showErrorState('Error connecting to server');
            
            // If API endpoint is not implemented yet, show mock data for development
            renderMockCharts(reportType, period);
        });
}

// Update the summary statistics
function updateReportStats(stats) {
    const statsContainer = document.getElementById('reportSummaryStats');
    if (!statsContainer) return;
    
    // Clear existing stats
    statsContainer.innerHTML = '';
    
    // Add stats
    if (stats && stats.length > 0) {
        stats.forEach(stat => {
            const statElement = document.createElement('div');
            statElement.className = 'data-stat';
            statElement.innerHTML = `
                <div class="value">${stat.value}</div>
                <div class="label">${stat.label}</div>
            `;
            statsContainer.appendChild(statElement);
        });
    } else {
        // Default stats if none provided
        const defaultStats = [
            { label: 'Total Products', value: '350' },
            { label: 'Low Stock Items', value: '27' },
            { label: 'Average Margin', value: '32%' },
            { label: 'Total Value', value: '$24,320' }
        ];
        
        defaultStats.forEach(stat => {
            const statElement = document.createElement('div');
            statElement.className = 'data-stat';
            statElement.innerHTML = `
                <div class="value">${stat.value}</div>
                <div class="label">${stat.label}</div>
            `;
            statsContainer.appendChild(statElement);
        });
    }
}

// Render charts based on the data
function renderCharts(reportType, period, data) {
    switch(reportType) {
        case 'seasonal':
            renderSeasonalCharts(period, data);
            break;
        case 'stockout':
            renderStockoutCharts(period, data);
            break;
        case 'pricing':
            renderPricingCharts(period, data);
            break;
        case 'reordering':
            renderReorderingCharts(period, data);
            break;
        case 'expiry':
            renderExpiryCharts(period, data);
            break;
        case 'sales':
            renderSalesCharts(period, data);
            break;
        case 'restructure':
            renderRestructureCharts(period, data);
            break;
        default:
            renderSeasonalCharts(period, data);
    }
}

// Show error state
function showErrorState(message) {
    const charts = [
        'priceDistributionChart',
        'competitorPriceChart',
        'priceElasticityChart',
        'profitMarginChart'
    ];
    
    charts.forEach(chartId => {
        const container = document.getElementById(chartId).parentNode;
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
            </div>
        `;
    });
}

// For development purposes - remove in production and implement actual API endpoints
function renderMockCharts(reportType, period) {
    // Create realistic looking data based on the report type and period
    const mockData = generateMockData(reportType, period);
    
    // Render charts with the mock data
    renderCharts(reportType, period, mockData);
    
    // Update stats
    updateReportStats(generateMockStats(reportType));
}

// Generate mock data for development
function generateMockData(reportType, period) {
    // Number of data points based on period
    let dataPoints;
    let labels = [];
    
    switch(period) {
        case 'daily':
            dataPoints = 24; // Hours in a day
            for (let i = 0; i < dataPoints; i++) {
                labels.push(`${i}:00`);
            }
            break;
        case 'weekly':
            dataPoints = 7; // Days in a week
            labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
            break;
        case 'monthly':
            dataPoints = 30; // Average days in a month
            for (let i = 1; i <= dataPoints; i++) {
                labels.push(`Day ${i}`);
            }
            break;
    }
    
    // Create datasets based on report type
    let datasets = [];
    let secondaryDatasets = [];
    let tertiaryDatasets = [];
    
    // Use colors that match the homepage theme
    const colors = [
        'rgba(0, 123, 255, 0.7)',  // Primary blue
        'rgba(252, 88, 42, 0.7)',   // Red/orange
        'rgba(40, 167, 69, 0.7)',  // Green
        'rgba(255, 193, 7, 0.7)',  // Yellow/warning
        'rgba(111, 66, 193, 0.7)', // Purple
        'rgba(23, 162, 184, 0.7)'  // Cyan/info
    ];
    
    switch(reportType) {
        case 'seasonal':
            // Main chart - Seasonal trends
            datasets.push({
                label: 'Food Items',
                data: generateRandomData(dataPoints, 100, 300),
                borderColor: colors[0],
                backgroundColor: colors[0],
                tension: 0.4
            });
            
            datasets.push({
                label: 'Electronics',
                data: generateRandomData(dataPoints, 50, 150),
                borderColor: colors[1],
                backgroundColor: colors[1],
                tension: 0.4
            });
            
            datasets.push({
                label: 'Clothing',
                data: generateRandomData(dataPoints, 75, 200),
                borderColor: colors[2],
                backgroundColor: colors[2],
                tension: 0.4
            });
            
            // Secondary chart - Category breakdown
            secondaryDatasets.push({
                label: 'Category Distribution',
                data: [35, 25, 20, 10, 10],
                backgroundColor: colors,
            });
            
            // Tertiary chart - YoY comparison
            tertiaryDatasets.push({
                label: 'This Year',
                data: generateRandomData(12, 100, 300),
                borderColor: colors[0],
                backgroundColor: colors[0],
                tension: 0.4
            });
            
            tertiaryDatasets.push({
                label: 'Last Year',
                data: generateRandomData(12, 75, 250),
                borderColor: colors[1],
                backgroundColor: colors[1],
                tension: 0.4
            });
            break;
            
        case 'stockout':
            // Main chart - Stockout risk
            datasets.push({
                label: 'High Risk Items',
                data: generateRandomData(dataPoints, 5, 15),
                borderColor: colors[1],
                backgroundColor: colors[1],
                tension: 0.1
            });
            
            datasets.push({
                label: 'Medium Risk Items',
                data: generateRandomData(dataPoints, 10, 30),
                borderColor: colors[3],
                backgroundColor: colors[3],
                tension: 0.1
            });
            
            datasets.push({
                label: 'Low Risk Items',
                data: generateRandomData(dataPoints, 40, 80),
                borderColor: colors[0],
                backgroundColor: colors[0],
                tension: 0.1
            });
            
            // Secondary chart - Stock level distribution
            secondaryDatasets.push({
                label: 'Stock Level Distribution',
                data: [15, 25, 60],
                backgroundColor: [colors[1], colors[3], colors[0]],
            });
            
            // Tertiary chart - Lead time analysis
            tertiaryDatasets.push({
                label: 'Average Lead Time (Days)',
                data: generateRandomData(10, 3, 15), // For different suppliers
                borderColor: colors[2],
                backgroundColor: colors[2],
                tension: 0.1
            });
            break;
            
        case 'pricing':
            // Main chart - Price elasticity
            datasets.push({
                label: 'Sales Volume',
                data: generateRandomData(dataPoints, 50, 200),
                borderColor: colors[0],
                backgroundColor: colors[0],
                tension: 0.3
            });
            
            datasets.push({
                label: 'Price Point',
                data: generateRandomData(dataPoints, 15, 45),
                borderColor: colors[3],
                backgroundColor: colors[3],
                tension: 0.3
            });
            
            // Secondary chart - Margin distribution by category
            secondaryDatasets.push({
                label: 'Margin Distribution',
                data: [25, 35, 20, 15, 5],
                backgroundColor: colors,
            });
            
            // Tertiary chart - Price comparison with competitors
            tertiaryDatasets.push({
                label: 'Our Prices',
                data: generateRandomData(5, 30, 50),
                borderColor: colors[0],
                backgroundColor: colors[0],
            });
            
            tertiaryDatasets.push({
                label: 'Competitor A',
                data: generateRandomData(5, 25, 55),
                borderColor: colors[1],
                backgroundColor: colors[1],
            });
            
            tertiaryDatasets.push({
                label: 'Competitor B',
                data: generateRandomData(5, 35, 60),
                borderColor: colors[2],
                backgroundColor: colors[2],
            });
            break;
            
        case 'reordering':
            // Main chart - Reorder point analysis
            datasets.push({
                label: 'Inventory Level',
                data: generateSinusoidalData(dataPoints, 50, 150),
                borderColor: colors[0],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                fill: true
            });
            
            datasets.push({
                label: 'Reorder Point',
                data: Array(dataPoints).fill(60),
                borderColor: colors[1],
                borderDashed: [5, 5],
                tension: 0,
                borderWidth: 2,
                fill: false
            });
            
            // Secondary chart - Categories needing reorder
            secondaryDatasets.push({
                label: 'Categories Needing Reorder',
                data: [12, 19, 8, 5, 2, 3],
                backgroundColor: colors,
            });
            
            // Tertiary chart - Order cycle time
            tertiaryDatasets.push({
                label: 'Order Cycle Time (Days)',
                data: generateRandomData(10, 2, 14),
                borderColor: colors[3],
                backgroundColor: colors[3],
                tension: 0.1
            });
            break;
            
        case 'expiry':
            // Main chart - Expiring items by date
            datasets.push({
                label: 'Items Expiring',
                data: generateRandomData(dataPoints, 0, 20),
                borderColor: colors[1],
                backgroundColor: colors[1],
                tension: 0.4
            });
            
            // Secondary chart - Expiry distribution by category
            secondaryDatasets.push({
                label: 'Expiry by Category',
                data: [45, 25, 20, 10],
                backgroundColor: colors,
            });
            
            // Tertiary chart - Value of expiring inventory
            tertiaryDatasets.push({
                label: 'Value of Expiring Inventory',
                data: generateRandomData(dataPoints, 100, 2000),
                borderColor: colors[3],
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
                tension: 0.4,
                fill: true
            });
            break;
            
        case 'sales':
            // Main chart - Sales trends
            datasets.push({
                label: 'Sales Volume',
                data: generateRandomData(dataPoints, 1000, 5000),
                borderColor: colors[0],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                fill: true
            });
            
            datasets.push({
                label: 'Average Order Value',
                data: generateRandomData(dataPoints, 50, 150),
                borderColor: colors[1],
                backgroundColor: colors[1],
                tension: 0.4,
                type: 'line',
                yAxisID: 'y1'
            });
            
            // Secondary chart - Sales by category
            secondaryDatasets.push({
                label: 'Sales by Category',
                data: [38, 22, 15, 10, 15],
                backgroundColor: colors,
            });
            
            // Tertiary chart - Top selling products
            tertiaryDatasets.push({
                label: 'Units Sold',
                data: [124, 118, 93, 85, 72, 65, 61, 55, 52, 48],
                backgroundColor: colors[2],
            });
            break;
            
        case 'restructure':
            // Main chart - Space utilization
            datasets.push({
                label: 'Space Utilization (%)',
                data: generateRandomData(dataPoints, 60, 95),
                borderColor: colors[2],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.4,
                fill: true
            });
            
            // Secondary chart - Category allocation
            secondaryDatasets.push({
                label: 'Category Space Allocation',
                data: [40, 25, 15, 10, 5, 5],
                backgroundColor: colors,
            });
            
            // Tertiary chart - Pick efficiency by location
            tertiaryDatasets.push({
                label: 'Pick Efficiency',
                data: generateRandomData(8, 50, 100),
                borderColor: colors[4],
                backgroundColor: colors[4],
            });
            break;
    }
    
    return {
        labels,
        datasets,
        secondaryLabels: reportType === 'seasonal' ? ['Food', 'Electronics', 'Clothing', 'Home', 'Other'] :
                         reportType === 'stockout' ? ['High Risk', 'Medium Risk', 'Low Risk'] :
                         reportType === 'pricing' ? ['0-10%', '11-20%', '21-30%', '31-40%', '41%+'] :
                         reportType === 'reordering' ? ['Food', 'Electronics', 'Clothing', 'Beauty', 'Home', 'Other'] :
                         reportType === 'expiry' ? ['This Week', 'Next Week', 'This Month', 'Next Month'] :
                         reportType === 'sales' ? ['Food', 'Electronics', 'Clothing', 'Beauty', 'Other'] :
                         reportType === 'restructure' ? ['Food', 'Electronics', 'Clothing', 'Beauty', 'Home', 'Other'] : [],
        secondaryDatasets,
        tertiaryLabels: reportType === 'seasonal' ? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] :
                        reportType === 'stockout' ? ['Supplier 1', 'Supplier 2', 'Supplier 3', 'Supplier 4', 'Supplier 5', 
                                                   'Supplier 6', 'Supplier 7', 'Supplier 8', 'Supplier 9', 'Supplier 10'] :
                        reportType === 'pricing' ? ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'] :
                        reportType === 'reordering' ? ['Supplier 1', 'Supplier 2', 'Supplier 3', 'Supplier 4', 'Supplier 5', 
                                                     'Supplier 6', 'Supplier 7', 'Supplier 8', 'Supplier 9', 'Supplier 10'] :
                        reportType === 'expiry' ? labels : // Use same labels as main chart
                        reportType === 'sales' ? ['Product 1', 'Product 2', 'Product 3', 'Product 4', 'Product 5', 
                                               'Product 6', 'Product 7', 'Product 8', 'Product 9', 'Product 10'] :
                        reportType === 'restructure' ? ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Zone F', 'Zone G', 'Zone H'] : [],
        tertiaryDatasets
    };
}

// Generate mock stats for development
function generateMockStats(reportType) {
    switch(reportType) {
        case 'seasonal':
            return [
                { label: 'Seasonal Products', value: '124' },
                { label: 'Peak Demand Increase', value: '+42%' },
                { label: 'Seasonal Revenue', value: '$12.4K' },
                { label: 'Stock Readiness', value: '87%' }
            ];
        case 'stockout':
            return [
                { label: 'Stockout Risk Items', value: '27' },
                { label: 'Critical Stock Level', value: '11' },
                { label: 'Avg Lead Time', value: '6 days' },
                { label: 'Potential Revenue Loss', value: '$5.2K' }
            ];
        case 'pricing':
            return [
                { label: 'Optimal Price Points', value: '32' },
                { label: 'Average Margin', value: '34%' },
                { label: 'Price Competitive Items', value: '87%' },
                { label: 'Potential Margin Gain', value: '+8%' }
            ];
        case 'reordering':
            return [
                { label: 'Items Below Reorder', value: '18' },
                { label: 'Auto Orders Generated', value: '7' },
                { label: 'Avg Days to Restock', value: '4.2' },
                { label: 'Order Value', value: '$3.8K' }
            ];
        case 'expiry':
            return [
                { label: 'Expiring This Month', value: '45' },
                { label: 'Critical Items', value: '12' },
                { label: 'Potential Loss', value: '$1.8K' },
                { label: 'Markdown Value', value: '$820' }
            ];
        case 'sales':
            return [
                { label: 'Total Sales', value: '$35.2K' },
                { label: 'Avg Order Value', value: '$87' },
                { label: 'Top Category', value: 'Food' },
                { label: 'Growth Rate', value: '+12%' }
            ];
        case 'restructure':
            return [
                { label: 'Space Utilization', value: '84%' },
                { label: 'Picking Efficiency', value: '+23%' },
                { label: 'Travel Distance', value: '-18%' },
                { label: 'Labor Cost Saving', value: '$1.2K' }
            ];
        default:
            return [
                { label: 'Total Products', value: '350' },
                { label: 'Low Stock Items', value: '27' },
                { label: 'Average Margin', value: '32%' },
                { label: 'Total Value', value: '$24.3K' }
            ];
    }
}

// Helper function to generate random data
function generateRandomData(length, min, max) {
    return Array.from({ length }, () => Math.floor(Math.random() * (max - min + 1)) + min);
}

// Helper function to generate sinusoidal data (looks more natural for inventory cycles)
function generateSinusoidalData(length, min, max) {
    const amplitude = (max - min) / 2;
    const offset = min + amplitude;
    const period = length / 1.5; // 1.5 cycles in the entire dataset
    
    return Array.from({ length }, (_, i) => {
        return Math.floor(offset + amplitude * Math.sin(2 * Math.PI * i / period));
    });
}

// Render charts for seasonal analysis
function renderSeasonalCharts(period, data) {
    // Main chart - line chart showing seasonal trends
    const mainCtx = document.getElementById('mainChart').getContext('2d');
    new Chart(mainCtx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Seasonal Demand Fluctuation (${capitalizeFirstLetter(period)})`
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Units Sold'
                    }
                }
            }
        }
    });
    
    // Secondary chart - doughnut chart showing category distribution
    const secondaryCtx = document.getElementById('secondaryChart').getContext('2d');
    new Chart(secondaryCtx, {
        type: 'doughnut',
        data: {
            labels: data.secondaryLabels,
            datasets: data.secondaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Category Distribution'
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
    
    // Tertiary chart - line chart showing year-over-year comparison
    const tertiaryCtx = document.getElementById('tertiaryChart').getContext('2d');
    new Chart(tertiaryCtx, {
        type: 'line',
        data: {
            labels: data.tertiaryLabels,
            datasets: data.tertiaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Year-over-Year Comparison'
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Units Sold'
                    }
                }
            }
        }
    });
}

// Render charts for stockout risk analysis
function renderStockoutCharts(period, data) {
    // Main chart - stacked bar chart showing stockout risk by category
    const mainCtx = document.getElementById('mainChart').getContext('2d');
    new Chart(mainCtx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Stockout Risk Analysis (${capitalizeFirstLetter(period)})`
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Number of Items'
                    }
                },
                x: {
                    stacked: true
                }
            }
        }
    });
    
    // Secondary chart - pie chart showing stock level distribution
    const secondaryCtx = document.getElementById('secondaryChart').getContext('2d');
    new Chart(secondaryCtx, {
        type: 'pie',
        data: {
            labels: data.secondaryLabels,
            datasets: data.secondaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Stock Level Distribution'
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
    
    // Tertiary chart - bar chart showing lead time by supplier
    const tertiaryCtx = document.getElementById('tertiaryChart').getContext('2d');
    new Chart(tertiaryCtx, {
        type: 'bar',
        data: {
            labels: data.tertiaryLabels,
            datasets: data.tertiaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: 'Lead Time by Supplier'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Average Days'
                    }
                }
            }
        }
    });
}

// Render charts for pricing optimization
function renderPricingCharts(period, data) {
    // Main chart - line chart showing price elasticity
    const mainCtx = document.getElementById('mainChart').getContext('2d');
    new Chart(mainCtx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Pricing Optimization Analysis (${capitalizeFirstLetter(period)})`
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Units Sold'
                    }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    title: {
                        display: true,
                        text: 'Price ($)'
                    }
                }
            }
        }
    });
    
    // Secondary chart - pie chart showing margin distribution
    const secondaryCtx = document.getElementById('secondaryChart').getContext('2d');
    new Chart(secondaryCtx, {
        type: 'pie',
        data: {
            labels: data.secondaryLabels,
            datasets: data.secondaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Margin Distribution'
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
    
    // Tertiary chart - bar chart showing price comparison
    const tertiaryCtx = document.getElementById('tertiaryChart').getContext('2d');
    new Chart(tertiaryCtx, {
        type: 'bar',
        data: {
            labels: data.tertiaryLabels,
            datasets: data.tertiaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Price Comparison with Competitors'
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Price ($)'
                    }
                }
            }
        }
    });
}

// Render charts for reordering analysis
function renderReorderingCharts(period, data) {
    // Main chart - line chart showing inventory cycles with reorder point
    const mainCtx = document.getElementById('mainChart').getContext('2d');
    new Chart(mainCtx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Reordering Analysis (${capitalizeFirstLetter(period)})`
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Inventory Level'
                    }
                }
            }
        }
    });
    
    // Secondary chart - bar chart showing categories needing reorder
    const secondaryCtx = document.getElementById('secondaryChart').getContext('2d');
    new Chart(secondaryCtx, {
        type: 'bar',
        data: {
            labels: data.secondaryLabels,
            datasets: data.secondaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Categories Needing Reorder'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Items'
                    }
                }
            }
        }
    });
    
    // Tertiary chart - horizontal bar chart showing order cycle time by supplier
    const tertiaryCtx = document.getElementById('tertiaryChart').getContext('2d');
    new Chart(tertiaryCtx, {
        type: 'bar',
        data: {
            labels: data.tertiaryLabels,
            datasets: data.tertiaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: 'Order Cycle Time by Supplier'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Days'
                    }
                }
            }
        }
    });
}

// Render charts for expiry tracking
function renderExpiryCharts(period, data) {
    // Main chart - line chart showing expiring items over time
    const mainCtx = document.getElementById('mainChart').getContext('2d');
    new Chart(mainCtx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Expiry Tracking (${capitalizeFirstLetter(period)})`
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Items'
                    }
                }
            }
        }
    });
    
    // Secondary chart - pie chart showing expiry by category
    const secondaryCtx = document.getElementById('secondaryChart').getContext('2d');
    new Chart(secondaryCtx, {
        type: 'pie',
        data: {
            labels: data.secondaryLabels,
            datasets: data.secondaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Expiry by Time Period'
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
    
    // Tertiary chart - area chart showing value of expiring inventory
    const tertiaryCtx = document.getElementById('tertiaryChart').getContext('2d');
    new Chart(tertiaryCtx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: data.tertiaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Value of Expiring Inventory'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Value ($)'
                    }
                }
            }
        }
    });
}

// Render charts for sales analytics
function renderSalesCharts(period, data) {
    // Main chart - combined line and bar chart for sales volume and AOV
    const mainCtx = document.getElementById('mainChart').getContext('2d');
    new Chart(mainCtx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Sales Analytics (${capitalizeFirstLetter(period)})`
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Sales Volume ($)'
                    }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    title: {
                        display: true,
                        text: 'Avg Order Value ($)'
                    }
                }
            }
        }
    });
    
    // Secondary chart - doughnut chart showing sales by category
    const secondaryCtx = document.getElementById('secondaryChart').getContext('2d');
    new Chart(secondaryCtx, {
        type: 'doughnut',
        data: {
            labels: data.secondaryLabels,
            datasets: data.secondaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Sales by Category'
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
    
    // Tertiary chart - horizontal bar chart showing top selling products
    const tertiaryCtx = document.getElementById('tertiaryChart').getContext('2d');
    new Chart(tertiaryCtx, {
        type: 'bar',
        data: {
            labels: data.tertiaryLabels,
            datasets: data.tertiaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: 'Top 10 Selling Products'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Units Sold'
                    }
                }
            }
        }
    });
}

// Render charts for inventory restructuring
function renderRestructureCharts(period, data) {
    // Main chart - line chart showing space utilization
    const mainCtx = document.getElementById('mainChart').getContext('2d');
    new Chart(mainCtx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Inventory Restructuring Analysis (${capitalizeFirstLetter(period)})`
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Space Utilization (%)'
                    },
                    max: 100
                }
            }
        }
    });
    
    // Secondary chart - pie chart showing category space allocation
    const secondaryCtx = document.getElementById('secondaryChart').getContext('2d');
    new Chart(secondaryCtx, {
        type: 'pie',
        data: {
            labels: data.secondaryLabels,
            datasets: data.secondaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Category Space Allocation'
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
    
    // Tertiary chart - horizontal bar chart showing pick efficiency by location
    const tertiaryCtx = document.getElementById('tertiaryChart').getContext('2d');
    new Chart(tertiaryCtx, {
        type: 'bar',
        data: {
            labels: data.tertiaryLabels,
            datasets: data.tertiaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Pick Efficiency by Zone'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Efficiency (%)'
                    },
                    max: 100
                }
            }
        }
    });
}

// Helper function to capitalize first letter
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function initializeNavigation() {
    const tabs = document.querySelectorAll('#reportTabs .nav-link');
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            const target = document.querySelector(this.getAttribute('href'));
            document.querySelectorAll('.tab-pane').forEach(p => {
                p.classList.remove('show', 'active');
            });
            target.classList.add('show', 'active');
            
            // Load data based on the selected tab
            const reportType = this.getAttribute('data-report-type');
            if (reportType === 'pricing') {
                loadPricingOptimizationData();
            } else if (reportType === 'seasonal') {
                loadSeasonalData();
            }
            // Add more report types as needed
        });
    });
}

function loadPricingOptimizationData() {
    fetch('/api/reports/pricing-optimization')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update price distribution chart
                if (data.data.price_distribution) {
                    updateChart('priceDistributionChart', data.data.price_distribution);
                }
                
                // Update competitor prices chart
                if (data.data.competitor_prices) {
                    updateChart('competitorPricesChart', data.data.competitor_prices);
                }
                
                // Update profit margins chart
                if (data.data.profit_margins) {
                    updateChart('profitMarginsChart', data.data.profit_margins);
                }
                
                // Update price differences table
                if (data.data.price_differences) {
                    const tableBody = document.getElementById('priceDifferencesTableBody');
                    tableBody.innerHTML = '';
                    
                    data.data.price_differences.forEach(item => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${item.label}</td>
                            <td>${formatCurrency(item.base_price)}</td>
                            <td>${formatCurrency(item.competitor_price)}</td>
                            <td class="${item.difference >= 0 ? 'text-success' : 'text-danger'}">
                                ${formatCurrency(item.difference)}
                            </td>
                        `;
                        tableBody.appendChild(row);
                    });
                }
            } else {
                showError('Failed to load pricing optimization data');
            }
        })
        .catch(error => {
            console.error('Error loading pricing optimization data:', error);
            showError('Failed to load pricing optimization data');
        });
}

function updateChart(chartId, chartData) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    // Destroy existing chart if it exists
    if (window[chartId]) {
        window[chartId].destroy();
    }
    
    // Create new chart
    window[chartId] = new Chart(ctx, {
        type: chartData.type,
        data: chartData.data,
        options: chartData.options
    });
}

function loadSeasonalData() {
    fetch('/api/reports/seasonal')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateSeasonalChart(data.data);
            } else {
                console.error('Error loading seasonal data:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function updateSeasonalChart(data) {
    const ctx = document.getElementById('seasonalChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (Chart.getChart(ctx)) {
        Chart.getChart(ctx).destroy();
    }
    
    new Chart(ctx, {
        type: data.type,
        data: data.data,
        options: data.options
    });
}

// Helper function to format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Helper function to format percentage
function formatPercentage(value) {
    return `${value.toFixed(1)}%`;
}

// Helper function to format date
function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

// Helper function to show error messages
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    document.querySelector('.content-wrapper').prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function handleSimulationData(event) {
    const { simulationType, data } = event.detail;
    
    // Hide no simulation message
    document.getElementById('noSimulationMessage').style.display = 'none';
    
    // Show chart and stats areas
    const chartElement = document.getElementById('simulationChart');
    chartElement.style.display = 'block';
    document.getElementById('reportStats').style.display = 'block';
    
    // Send simulation data to backend for processing
    fetch('/api/reports/process-simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            simulation_type: simulationType,
            data: data
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            // Update chart
            chartElement.src = `data:image/png;base64,${result.chart}`;
            
            // Update stats
            updateStats(result.stats);
        } else {
            showError(result.message || 'Failed to process simulation data');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error processing simulation data');
    });
}

function updateStats(stats) {
    const container = document.querySelector('.stats-container');
    container.innerHTML = '';
    
    stats.forEach(stat => {
        const statElement = document.createElement('div');
        statElement.className = 'stat-item';
        statElement.innerHTML = `
            <div class="stat-value">${stat.value}</div>
            <div class="stat-label">${stat.label}</div>
        `;
        container.appendChild(statElement);
    });
}

function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger';
    alertDiv.textContent = message;
    
    const chartArea = document.getElementById('reportChartArea');
    chartArea.innerHTML = '';
    chartArea.appendChild(alertDiv);
}

function generateSimulationData(type, items, period = 'weekly') {
    // Instead of generating simulated data, just pass the real items and period to the backend
    return {
        items: items,
        period: period
    };
}



