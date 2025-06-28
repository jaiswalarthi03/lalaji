// Inventory Management JavaScript
// Import utilities
// <script src="/static/js/utils.js"></script> should be included in HTML

// Use utility functions from utils.js for chart, error, fetch, and row updates
// Example usage in simulation functions:
// updateTableRow(row, (r) => { ... });
// showChartError('inventoryChart', 'Error message');
// fetchData('/api/inventory').then(...)

document.addEventListener('DOMContentLoaded', function() {
    // Initialize inventory features
    initializeInventoryUpload();
    loadInventoryData();
    setupFilterButtons();
    setupSimulation();
    
    // Connect save button to form submission
    const saveProductBtn = document.getElementById('saveProductBtn');
    if (saveProductBtn) {
        saveProductBtn.addEventListener('click', function() {
            addProductFromForm();
        });
    }
    const storeDropdown = document.getElementById('storeFlagsDropdown');
    if (storeDropdown) {
        storeDropdown.addEventListener('change', function () {
            location.reload();
            const selectedStore = this.value; // Get the selected store value
            const currentUrl = window.location.href.split('?')[0]; // Remove existing query parameters
            window.location.href = `${currentUrl}?store=${selectedStore}`; // Reload with the selected store
        });
    }
});
 
// Upload functionality
function initializeInventoryUpload() {
    // Barcode upload area click handler
    const barcodeUploadArea = document.getElementById('barcodeUploadArea');
    const barcodeFileInput = document.getElementById('barcodeFileInput');
    const barcodePreview = document.getElementById('barcodePreview');
    const previewImage = document.getElementById('previewImage');
    const removeBarcodeBtn = document.getElementById('removeBarcodeBtn');
   
    if (barcodeUploadArea && barcodeFileInput) {
        barcodeUploadArea.addEventListener('click', function() {
            barcodeFileInput.click();
        });
       
        barcodeFileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const reader = new FileReader();
               
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    barcodePreview.style.display = 'flex';
                    barcodeUploadArea.style.display = 'none';
                   
                    // Process the image with Gemini API automatically
                    // Show processing notification
                    const notification = showProcessingNotification('Processing product image...');
                   
                    // Create FormData and append the file
                    const formData = new FormData();
                    formData.append('product_image', file);
                   
                    // Send to server for processing
                    fetch('/api/inventory/process-image', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Remove processing notification
                        notification.remove();
                       
                        if (data.status === 'success' && data.product_details) {
                            // Show product details modal
                            const productModal = new bootstrap.Modal(document.getElementById('productDetailsModal'));
                           
                            // Fill in the form fields with recognized data
                            document.getElementById('productName').value = data.product_details.product_name || '';
                            document.getElementById('productBrand').value = data.product_details.brand || '';
                            document.getElementById('productCategory').value = data.product_details.category || 'Food';
                            document.getElementById('productSKU').value =
                                data.product_details.brand ?
                                (data.product_details.brand.substring(0,2) + Math.floor(1000 + Math.random() * 9000)).toUpperCase() :
                                ('PD' + Math.floor(1000 + Math.random() * 9000));
                            document.getElementById('productQuantity').value = '10'; // Default quantity
                            document.getElementById('productPrice').value = data.product_details.estimated_price || '5.00';
                            document.getElementById('productCostPrice').value =
                                (parseFloat(data.product_details.estimated_price || 5.0) * 0.8).toFixed(2);
                           
                            // Show the modal
                            productModal.show();
                           
                            showSuccessNotification('Product recognized successfully');
                        } else {
                            // Show modal with generic data
                            const productModal = new bootstrap.Modal(document.getElementById('productDetailsModal'));
                            document.getElementById('productName').value = 'New Product';
                            document.getElementById('productBrand').value = '';
                            document.getElementById('productCategory').value = 'Food';
                            document.getElementById('productSKU').value = 'PD' + Math.floor(1000 + Math.random() * 9000);
                            document.getElementById('productQuantity').value = '10';
                            document.getElementById('productPrice').value = '5.00';
                            document.getElementById('productCostPrice').value = '4.00';
                            productModal.show();
                           
                            showErrorNotification(data.message || 'Could not recognize product, please enter details manually');
                        }
                    })
                    .catch(error => {
                        notification.remove();
                        console.error('Error:', error);
                        showErrorNotification('Error processing image');
                    });
                };
               
                reader.readAsDataURL(file);
            }
        });
       
        // Remove barcode image
        if (removeBarcodeBtn) {
            removeBarcodeBtn.addEventListener('click', function() {
                barcodeFileInput.value = '';
                barcodePreview.style.display = 'none';
                barcodeUploadArea.style.display = 'block';
            });
        }
    }
   
    // Excel upload area handler
    const excelUploadArea = document.getElementById('excelUploadArea');
    const excelFileInput = document.getElementById('excelFileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const processBtn = document.getElementById('processInventoryBtn');
   
    if (excelUploadArea && excelFileInput) {
        excelUploadArea.addEventListener('click', () => excelFileInput.click());
       
        excelFileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                fileName.textContent = file.name;
                fileInfo.style.display = 'flex';
                excelUploadArea.style.display = 'none';
            }
        });
       
        // Remove excel file
        removeFileBtn?.addEventListener('click', function() {
            excelFileInput.value = '';
            fileInfo.style.display = 'none';
            excelUploadArea.style.display = 'block';
        });
    }
   
   

    // Process button handler
if (processBtn) {
    processBtn.addEventListener('click', async function() {
        const excelFile = excelFileInput?.files?.[0];

        if (excelFile) {
            // Show processing notification
            const notification = showProcessingNotification('Processing inventory update...');

            try {
                // Create FormData and append the file
                const formData = new FormData();
                formData.append('inventory_file', excelFile);

                // Send to server for processing
                const response = await fetch('/api/inventory/update', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                // Safely remove notification
                if (notification && notification.parentNode) {
                    notification.remove();
                }

                if (data.status === 'success') {
                    // Show success notification
                    showSuccessNotification(data.message || 'Purchase information added to inventory successfully');

                    // Clear the file input and reset display
                    excelFileInput.value = '';
                    fileInfo.style.display = 'none';
                    excelUploadArea.style.display = 'block';

                    // Add small delay before updating UI to prevent conflicts
                    setTimeout(async () => {
                        try {
                            // Update UI in sequence to ensure proper refresh
                            await loadInventoryData(); // Refresh the inventory data
                            await updateInventoryStats(); // Update the inventory stats display
                        } catch (refreshError) {
                            console.error('Error refreshing data:', refreshError);
                            // Don't show error notification for refresh issues
                        }
                    }, 300);
                } else {
                    throw new Error(data.message || 'Error updating inventory');
                }
            } catch (error) {
                // Safely remove notification if it still exists
                if (notification && notification.parentNode) {
                    notification.remove();
                }
                
                console.error('Error:', error);
                showErrorNotification(error.message || 'Error processing purchase document');
            }
        } else {
            showErrorNotification('Please upload a purchase document first');
        }
    });
}

}

function loadInventoryData() {
    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    // Show loading state
    tableBody.innerHTML = '<tr><td colspan="12" class="text-center py-4"><i class="fas fa-spinner fa-spin me-2"></i> Loading inventory data...</td></tr>';
    
    // Fetch inventory data
    fetch('/api/inventory')
        .then(response => {
            console.log('api response status', response.status);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
             return response.json();
            })
        .then(data => {
            console.log("data", data)
            console.log("data.items",data.items);
            if(data.items){
                
                renderInventoryTable(data.items);
                updateInventoryStats(data.items);
            }
            else {
                console.error('Invalid data format:', data);
                tableBody.innerHTML = '<tr><td colspan="12" class="text-center py-4 text-danger">No inventory items found</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error fetching inventory data:', error);
            
           
        });
}

// Render inventory table
function renderInventoryTable(items) {
    console.log("Items", items);

    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (items.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="12" class="text-center py-4">No inventory items found</td></tr>';
        return;
    }
    
    items.forEach(item => {
        console.log("item from loop", item)

        const price = parseFloat(item.price.replace(/[^\d.-]/g, '')); // Removes non-numeric characters
        const costPrice = parseFloat(item.cost_price.replace(/[^\d.-]/g, '')); // Removes non-numeric characters


        // Calculate profit margin
        const margin = ((price - costPrice) / price * 100).toFixed(1);
        console.log("margin", margin)
        
        // Determine stock status
        let statusClass = 'status-ok';
        let statusText = 'In Stock';
        
        if (item.quantity <= item.reorder_level * 0.5) {
            statusClass = 'status-low';
            statusText = 'Out of Stock';
        } else if (item.quantity <= item.reorder_level) {
            statusClass = 'status-warning';
            statusText = 'Reorder';
        }
        
        // Format date
        const updatedDate = new Date(item.last_updated);
        const formattedDate = updatedDate.toLocaleDateString() + ' ' + 
                             updatedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        const row = document.createElement('tr');
        row.dataset.id = item.id;
        row.dataset.status = statusClass.split('-')[1]; // For filtering
        
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${item.sku}</td>
            <td>${item.category}</td>
            <td>${item.quantity}</td>
            <td>
                <div class="status-cell">
                    <span class="status-indicator ${statusClass}"></span>
                    ${statusText}
                </div>
            </td>
            <td>${item.price}</td>
            <td>${item.cost_price}</td>
            <td>${margin}%</td>
            <td>${item.reorder_level}</td>
            <td>${formattedDate}</td>
           
        `;
        
        tableBody.appendChild(row);
    });
}


// Setup filter buttons
function setupFilterButtons() {
    const lowStockBtn = document.getElementById('lowStockBtn');
    const inStockBtn = document.getElementById('inStockBtn');
    const allItemsBtn = document.getElementById('allItemsBtn');
    const inventorySearch = document.getElementById('inventorySearch');
   
    if (lowStockBtn && inStockBtn && allItemsBtn) {
        lowStockBtn.addEventListener('click', function() {
            setActiveFilterButton(this);
            filterInventoryItems('low');
        });
       
        inStockBtn.addEventListener('click', function() {
            setActiveFilterButton(this);
            filterInventoryItems('in');
        });
       
        allItemsBtn.addEventListener('click', function() {
            setActiveFilterButton(this);
            filterInventoryItems('all');
        });
       
        // Set initial active filter
        setActiveFilterButton(allItemsBtn);
    }
   
    if (inventorySearch) {
        inventorySearch.addEventListener('input', function() {
            searchInventoryItems(this.value);
        });
    }
}
 
// Function to set the active filter button
function setActiveFilterButton(button) {
    const filterButtons = document.querySelectorAll('.filter-buttons .btn');
    filterButtons.forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });

    button.classList.remove('btn-outline-primary');
    button.classList.add('btn-primary');
}

// Function to filter inventory items by status
function filterInventoryItems(status) {
    const rows = document.querySelectorAll('#inventoryTableBody tr');

    rows.forEach(row => {
        const quantityCell = row.querySelector('td:nth-child(5)'); // Quantity cell
        const reorderCell = row.querySelector('td:nth-child(10)'); // Reorder level cell

        if (!quantityCell || !reorderCell) {
            row.style.display = ''; // Show error/empty state rows
            return;
        }

        const quantity = parseInt(quantityCell.textContent.trim(), 10); // Get the quantity
        const reorderLevel = parseInt(reorderCell.textContent.trim(), 10); // Get the reorder level

        // Determine if the row should be displayed based on the status
        if (status === 'low' && quantity <= reorderLevel) {
            row.style.display = ''; // Show low stock items
        } else if (status === 'in' && quantity > reorderLevel) {
            row.style.display = ''; // Show in stock items
        } else if (status === 'all') {
            row.style.display = ''; // Show all items
        } else {
            row.style.display = 'none'; // Hide other items
        }
    });
}

// Setup filter buttons
function setupFilterButtons() {
    const lowStockBtn = document.getElementById('lowStockBtn');
    const inStockBtn = document.getElementById('inStockBtn');
    const allItemsBtn = document.getElementById('allItemsBtn');
    const inventorySearch = document.getElementById('inventorySearch');

    if (lowStockBtn && inStockBtn && allItemsBtn) {
        lowStockBtn.addEventListener('click', function() {
            setActiveFilterButton(this);
            filterInventoryItems('low');
        });

        inStockBtn.addEventListener('click', function() {
            setActiveFilterButton(this);
            filterInventoryItems('in');
        });

        allItemsBtn.addEventListener('click', function() {
            setActiveFilterButton(this);
            filterInventoryItems('all');
        });

        // Set initial active filter
        setActiveFilterButton(allItemsBtn);
    }

    if (inventorySearch) {
        inventorySearch.addEventListener('input', function() {
            searchInventoryItems(this.value);
        });
    }
}

// Call the setup function on page load
document.addEventListener('DOMContentLoaded', setupFilterButtons);

 
// Search inventory items
function searchInventoryItems(term) {
    const rows = document.querySelectorAll('#inventoryTableBody tr');
    const lowerTerm = term.toLowerCase();
   
    rows.forEach(row => {
        const nameCell = row.querySelector('td:nth-child(2)');
        const skuCell = row.querySelector('td:nth-child(3)');
        const categoryCell = row.querySelector('td:nth-child(4)');
       
        if (!nameCell || !skuCell || !categoryCell) {
            row.style.display = ''; // Show error/empty state rows
            return;
        }
       
        const nameText = nameCell.textContent.toLowerCase();
        const skuText = skuCell.textContent.toLowerCase();
        const categoryText = categoryCell.textContent.toLowerCase();
       
        if (nameText.includes(lowerTerm) || skuText.includes(lowerTerm) || categoryText.includes(lowerTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}



function setupSimulation() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const simulationSelect = document.getElementById('simulationSelect');
    const tableBody = document.getElementById('inventoryTableBody');
    let currentSelection = '';

    if (analyzeBtn && simulationSelect) {
        // Listen for dropdown changes
        simulationSelect.addEventListener('change', function() {
            // Clear the info row when selection changes
            const existingInfoRow = tableBody.querySelector('.simulation-info-row');
            if (existingInfoRow) {
                existingInfoRow.remove();
            }
            currentSelection = this.value; // Store the current selection
        });

        analyzeBtn.addEventListener('click', function() {
            if (currentSelection) {
                showProcessingNotification('Running simulation...');
                
                // Simulate processing delay
                setTimeout(() => {
                    runSimulation(currentSelection);
                    showSuccessNotification('Simulation complete');
                }, 1500);
            }
        });
    }
}

// Run inventory simulation
function runSimulation(type) {
    // Get current inventory data
    const rows = document.querySelectorAll('#inventoryTableBody tr');
    const items = [];
    
    rows.forEach(row => {
        if (row.cells && row.cells.length >= 5) {
            const id = row.cells[0].textContent;
            const name = row.cells[1].textContent;
            const sku = row.cells[2].textContent;
            const category = row.cells[3].textContent;
            const quantity = parseInt(row.cells[4].textContent);
            const price = parseFloat(row.cells[6].textContent.replace('₹', ''));
            const cost = parseFloat(row.cells[7].textContent.replace('₹', ''));
            const reorderLevel = parseInt(row.cells[9].textContent);
            
            items.push({ 
                id, 
                name, 
                sku,
                category,
                quantity, 
                price,
                cost,
                reorderLevel
            });
        }
    });
    
    // Apply simulation based on type
    switch (type) {
        case 'seasonal':
            applySeasionalSimulation(items);
            break;
        case 'stockout':
            applyStockoutSimulation(items);
            break;
        case 'pricing':
            applyPricingSimulation();
            break;
        case 'reordering':
            applyReorderingAnalysis(items);
            break;
        case 'expiry':
            applyExpiryTracking(items);
            break;
        case 'sales':
            applySalesAnalytics(items);
            break;
        case 'restructure':
            applyInventoryRestructuring(items);
            break;
    }
}

// Apply seasonal demand simulation
function applySeasionalSimulation(items) {
    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    // Create a simulation info row
    const infoRow = document.createElement('tr');
    infoRow.classList.add('simulation-info-row');
    infoRow.innerHTML = `
        <td colspan="12" class="p-3 bg-info text-white">
            <i class="fas fa-chart-line me-2"></i>
            <strong>Seasonal Demand Simulation:</strong> Showing projected inventory based on historical seasonal patterns.
            <button class="btn btn-sm btn-light ms-3" onclick="loadInventoryData()">Reset</button>
        </td>
    `;
    
    // Insert at the top of the table
    tableBody.insertBefore(infoRow, tableBody.firstChild);
    
    // Modify quantity columns with seasonal projections
    items.forEach(item => {
        const row = document.querySelector(`tr[data-id="${item.id}"]`);
        if (row && row.cells && row.cells.length >= 5) {
            const quantityCell = row.cells[4];
            const currentQuantity = parseInt(quantityCell.textContent);
            
            // Apply seasonal factor (example: holiday season increases demand by 40-80%)
            const seasonalFactor = 1 + (Math.random() * 0.4 + 0.4);
            const projectedQuantity = Math.max(0, Math.round(currentQuantity - (currentQuantity / seasonalFactor)));
            
            // Show projected quantity with comparison
            quantityCell.innerHTML = `
                <span style="text-decoration: line-through; color: #777;">${currentQuantity}</span>
                → <strong>${projectedQuantity}</strong>
                <small class="text-danger d-block">-${Math.round((currentQuantity - projectedQuantity) / currentQuantity * 100)}%</small>
            `;
            
            // Update status cell based on projected quantity
            const statusCell = row.cells[5];
            if (projectedQuantity <= item.reorderLevel * 0.5) {
                statusCell.innerHTML = `
                    <div class="status-cell">
                        <span class="status-indicator status-low"></span>
                        Critical (Projected)
                    </div>
                `;
            } else if (projectedQuantity <= item.reorderLevel) {
                statusCell.innerHTML = `
                    <div class="status-cell">
                        <span class="status-indicator status-warning"></span>
                        Low Stock (Projected)
                    </div>
                `;
            }
        }
    });
}

// Apply stockout risk simulation
function applyStockoutSimulation(items) {
    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    // Create a simulation info row
    const infoRow = document.createElement('tr');
    infoRow.classList.add('simulation-info-row');
    infoRow.innerHTML = `
        <td colspan="12" class="p-3 bg-warning text-white">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Stockout Risk Analysis:</strong> Showing items with high risk of stockout in the next 30 days.
            <button class="btn btn-sm btn-light ms-3" onclick="loadInventoryData()">Reset</button>
        </td>
    `;
    
    // Insert at the top of the table
    tableBody.insertBefore(infoRow, tableBody.firstChild);
    
    // Sort rows by stockout risk (low quantity to reorder level ratio)
    const rows = Array.from(tableBody.querySelectorAll('tr:not(.simulation-info-row)'));
    
    rows.sort((a, b) => {
        const aData = items.find(item => item.id === a.dataset.id);
        const bData = items.find(item => item.id === b.dataset.id);
        
        if (!aData || !bData) return 0;
        
        // Calculate risk scores (lower quantity/reorderLevel is higher risk)
        const aRisk = aData.quantity / aData.reorderLevel;
        const bRisk = bData.quantity / bData.reorderLevel;
        
        return aRisk - bRisk;
    });
    
    // Clear and re-append rows in new order
    rows.forEach(row => tableBody.appendChild(row));
    
    // Highlight stockout risks
    items.forEach(item => {
        const row = document.querySelector(`tr[data-id="${item.id}"]`);
        if (!row) return;
        
        // Calculate days until stockout at current consumption rate
        const dailyUsage = Math.max(1, Math.ceil(item.reorderLevel / 15)); // Approximate daily usage
        const daysToStockout = Math.round(item.quantity / dailyUsage);
        
        // Add stockout prediction
        const daysCell = document.createElement('td');
        daysCell.colSpan = "2";
        daysCell.innerHTML = `
            <div class="stockout-prediction">
                <strong>${daysToStockout} days</strong> until stockout
                <div class="progress mt-1" style="height: 6px;">
                    <div class="progress-bar ${daysToStockout < 10 ? 'bg-danger' : daysToStockout < 20 ? 'bg-warning' : 'bg-success'}" 
                         style="width: ${Math.min(100, daysToStockout * 3)}%"></div>
                </div>
            </div>
        `;
        
        // Replace last updated and reorder level cells with days to stockout
        if (row.cells && row.cells.length >= 11) {
            row.deleteCell(10); // Last updated
            row.deleteCell(9); // Reorder level
            row.insertBefore(daysCell, row.cells[9]);
        }
    });
}

// Apply pricing optimization simulation
function applyPricingSimulation() {
    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    // Create a simulation info row
    const infoRow = document.createElement('tr');
    infoRow.classList.add('simulation-info-row');
    infoRow.innerHTML = `
        <td colspan="12" class="p-3 bg-success text-white">
            <i class="fas fa-tags me-2"></i>
            <strong>Pricing Optimization:</strong> Suggested price adjustments to maximize profitability.
            <button class="btn btn-sm btn-light ms-3" onclick="loadInventoryData()">Reset</button>
        </td>
    `;
    
    // Insert at the top of the table
    tableBody.insertBefore(infoRow, tableBody.firstChild);
    
    // Optimize pricing for each product
    const rows = tableBody.querySelectorAll('tr:not(.simulation-info-row)');
    
    rows.forEach(row => {
        if (row.cells && row.cells.length >= 8) {
            const priceCell = row.cells[6];
            const costCell = row.cells[7];
            const marginCell = row.cells[8];
            
            // Current values
            const currentPrice = parseFloat(priceCell.textContent.replace('₹', ''));
            const cost = parseFloat(costCell.textContent.replace('₹', ''));
            const currentMargin = parseFloat(marginCell.textContent.replace('%', ''));
            
            // Calculate optimized price (simulated)
            const optimizationType = Math.floor(Math.random() * 3);
            let newPrice, marginChange, newMargin;
            
            if (optimizationType === 0) {
                // Increase price for premium positioning
                newPrice = currentPrice * (1 + (Math.random() * 0.15 + 0.05)).toFixed(2);
                newMargin = ((newPrice - cost) / newPrice * 100).toFixed(1);
                marginChange = (newMargin - currentMargin).toFixed(1);
                
                priceCell.innerHTML = `
                    <span style="text-decoration: line-through; color: #777;">₹${currentPrice.toFixed(2)}</span>
                    → <strong class="text-success">₹${newPrice.toFixed(2)}</strong>
                    <small class="text-success d-block">+${((newPrice - currentPrice) / currentPrice * 100).toFixed(1)}%</small>
                `;
                
                marginCell.innerHTML = `
                    <span style="text-decoration: line-through; color: #777;">${currentMargin}%</span>
                    → <strong class="text-success">${newMargin}%</strong>
                    <small class="text-success d-block">+${marginChange}%</small>
                `;
            } else if (optimizationType === 1) {
                // Decrease price for volume sales
                newPrice = currentPrice * (1 - (Math.random() * 0.1 + 0.02)).toFixed(2);
                newMargin = ((newPrice - cost) / newPrice * 100).toFixed(1);
                marginChange = (newMargin - currentMargin).toFixed(1);
                
                priceCell.innerHTML = `
                    <span style="text-decoration: line-through; color: #777;">₹${currentPrice.toFixed(2)}</span>
                    → <strong class="text-primary">₹${newPrice.toFixed(2)}</strong>
                    <small class="text-primary d-block">-${((currentPrice - newPrice) / currentPrice * 100).toFixed(1)}%</small>
                `;
                
                marginCell.innerHTML = `
                    <span style="text-decoration: line-through; color: #777;">${currentMargin}%</span>
                    → <strong>${newMargin}%</strong>
                    <small class="text-danger d-block">${marginChange}%</small>
                `;
            } else {
                // Maintain price (already optimal)
                priceCell.innerHTML = `
                    <strong>₹${currentPrice.toFixed(2)}</strong>
                    <small class="text-muted d-block">Optimal</small>
                `;
                
                marginCell.innerHTML = `
                    <strong>${currentMargin}%</strong>
                    <small class="text-muted d-block">Optimal</small>
                `;
            }
        }
    });
}

// Apply reordering analysis simulation
function applyReorderingAnalysis(items) {
    console.log("Starting reordering analysis for", items.length, "items");
    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    // Create a simulation info row
    const infoRow = document.createElement('tr');
    infoRow.classList.add('simulation-info-row');
    infoRow.innerHTML = `
        <td colspan="12" class="p-3 bg-primary text-white">
            <i class="fas fa-shopping-cart me-2"></i>
            <strong>Reordering Analysis:</strong> AI-calculated quantities and one-click reordering recommendations.
            <button class="btn btn-sm btn-light ms-3" onclick="loadInventoryData()">Reset</button>
        </td>
    `;
    
    // Insert at the top of the table
    tableBody.insertBefore(infoRow, tableBody.firstChild);
    
    try {
        // Update table headers to include reordering columns
        const headerRow = document.querySelector('#inventoryTable thead tr');
        if (headerRow) {
            // Add columns for Action if they don't exist already
            if (!headerRow.querySelector('th:last-child')) {
                const actionHeader = document.createElement('th');
                actionHeader.textContent = 'Action';
                headerRow.appendChild(actionHeader);
            }
            
            // Replace or update the last two columns
            const lastCell = headerRow.querySelector('th:last-child');
            const secondLastCell = headerRow.querySelector('th:nth-last-child(2)');
            
            if (lastCell) lastCell.textContent = 'Action';
            if (secondLastCell) secondLastCell.textContent = 'Suggested Reorder';
        }
        
        // Process each row to add reordering recommendations
        items.forEach(item => {
            const row = document.querySelector(`tr[data-id="${item.id}"]`);
            if (!row) return;
            
            // Calculate suggested reorder quantity
            const optimalOrderQty = Math.max(
                Math.ceil(item.reorderLevel * 1.5),
                Math.ceil((item.reorderLevel - item.quantity) * 1.2)
            );
            
            // Calculate priority level based on current stock vs reorder level
            const stockRatio = item.quantity / item.reorderLevel;
            let priorityClass, priorityText;
            
            if (stockRatio <= 0.5) {
                priorityClass = 'danger';
                priorityText = 'Critical';
            } else if (stockRatio <= 1) {
                priorityClass = 'warning';
                priorityText = 'High';
            } else if (stockRatio <= 1.5) {
                priorityClass = 'info';
                priorityText = 'Medium';
            } else {
                priorityClass = 'success';
                priorityText = 'Low';
            }
            
            // Make sure we have at least the minimum number of cells
            while (row.cells.length < 11) {
                row.appendChild(document.createElement('td'));
            }
            
            // Create reorder quantity cell
            const reorderQtyCell = document.createElement('td');
            reorderQtyCell.innerHTML = `
                <div class="d-flex align-items-center">
                    <input type="number" class="form-control form-control-sm" value="${optimalOrderQty}" min="1" style="width: 70px;">
                    <span class="ms-2 badge bg-${priorityClass}">${priorityText}</span>
                </div>
                <small class="text-muted d-block">Lead time: 3-5 days</small>
            `;
            
            // Create reorder action cell
            const actionCell = document.createElement('td');
            actionCell.innerHTML = `
                <button class="btn btn-sm btn-success" onclick="alert('Order placed for ${item.name}')">
                    <i class="fas fa-cart-plus me-1"></i> Order
                </button>
            `;
            
            // Replace or add cells as needed
            if (row.cells.length >= 11) {
                if (row.cells.length > 11) {
                    // If we have more than 11 cells, replace the last two
                    row.replaceChild(actionCell, row.cells[row.cells.length - 1]);
                    row.replaceChild(reorderQtyCell, row.cells[row.cells.length - 2]);
                } else {
                    // If we have exactly 11 cells, remove the last one and add our two new ones
                    row.removeChild(row.cells[row.cells.length - 1]);
                    row.appendChild(reorderQtyCell);
                    row.appendChild(actionCell);
                }
            } else {
                // If we have fewer than 11 cells, just append the new ones
                row.appendChild(reorderQtyCell);
                row.appendChild(actionCell);
            }
        });
        
        console.log("Reordering analysis completed successfully");
    } catch (error) {
        console.error("Error in reordering analysis:", error);
        showErrorNotification("Error applying reordering analysis: " + error.message);
    }
}

// Apply expiry tracking simulation
function applyExpiryTracking(items) {
    console.log("Starting expiry tracking for", items.length, "items");
    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    // Create a simulation info row
    const infoRow = document.createElement('tr');
    infoRow.classList.add('simulation-info-row');
    infoRow.innerHTML = `
        <td colspan="12" class="p-3 bg-danger text-white">
            <i class="fas fa-calendar-alt me-2"></i>
            <strong>Expiry Tracking:</strong> Monitoring product expiration dates with FIFO implementation.
            <button class="btn btn-sm btn-light ms-3" onclick="loadInventoryData()">Reset</button>
        </td>
    `;
    
    // Insert at the top of the table
    tableBody.insertBefore(infoRow, tableBody.firstChild);
    
    try {
        // Update table headers for expiry info
        const headerRow = document.querySelector('#inventoryTable thead tr');
        if (headerRow) {
            // Clear the existing header cells except for the first 9
            const headerCells = headerRow.querySelectorAll('th');
            for (let i = headerCells.length - 1; i >= 9; i--) {
                if (headerCells[i]) {
                    headerCells[i].remove();
                }
            }
            
            // Add new header cells
            const batchHeader = document.createElement('th');
            batchHeader.textContent = 'Batch Info';
            headerRow.appendChild(batchHeader);
            
            const expiryHeader = document.createElement('th');
            expiryHeader.textContent = 'Expiry Status';
            headerRow.appendChild(expiryHeader);
            
            const actionHeader = document.createElement('th');
            actionHeader.textContent = 'Action';
            headerRow.appendChild(actionHeader);
        }
        
        // Add expiry data to each item
        items.forEach(item => {
            const row = document.querySelector(`tr[data-id="${item.id}"]`);
            if (!row) return;
            
            // Create simulated batch and expiry data
            // Generate multiple batches with different expiry dates
            const batches = [];
            let remainingQty = item.quantity;
            const today = new Date();
            
            // Generate 1-3 batches per product
            const batchCount = Math.floor(Math.random() * 3) + 1;
            
            for (let i = 0; i < batchCount && remainingQty > 0; i++) {
                // Create random expiry date
                const expiryDate = new Date();
                
                // Different product categories have different shelf lives
                let daysToAdd;
                if (item.category === 'Dairy') {
                    daysToAdd = Math.floor(Math.random() * 30) + 5; // 5-35 days
                } else if (item.category === 'Confectionery') {
                    daysToAdd = Math.floor(Math.random() * 90) + 30; // 30-120 days
                } else {
                    daysToAdd = Math.floor(Math.random() * 180) + 60; // 60-240 days
                }
                
                expiryDate.setDate(today.getDate() + daysToAdd);
                
                // Assign quantity to this batch
                const batchQty = i === batchCount - 1 ? 
                    remainingQty : 
                    Math.floor(Math.random() * remainingQty * 0.7) + 1;
                
                remainingQty -= batchQty;
                
                // Generate batch ID
                const batchId = `B${item.id}${i+1}-${expiryDate.getMonth()+1}${expiryDate.getFullYear().toString().substr(2)}`;
                
                batches.push({
                    id: batchId,
                    quantity: batchQty,
                    expiryDate: expiryDate,
                    daysLeft: Math.floor((expiryDate - today) / (1000 * 60 * 60 * 24))
                });
            }
            
            // Sort batches by expiry date (FIFO)
            batches.sort((a, b) => a.daysLeft - b.daysLeft);
            
            // Make sure we have at least the minimum number of cells
            while (row.cells.length < 9) {
                row.appendChild(document.createElement('td'));
            }
            
            // Remove any cells beyond the 9th one (we'll add our 3 new ones)
            while (row.cells.length > 9) {
                row.deleteCell(row.cells.length - 1);
            }
            
            // Add batch info cell
            const batchCell = document.createElement('td');
            batchCell.innerHTML = `
                <div class="batch-info">
                    ${batches.map(batch => `
                        <div class="mb-1">
                            <small class="d-block"><strong>${batch.id}</strong> (${batch.quantity} units)</small>
                        </div>
                    `).join('')}
                </div>
            `;
            row.appendChild(batchCell);
            
            // Add expiry status cell
            const expiryCell = document.createElement('td');
            
            // Check for expired or near-expiry products
            const hasExpired = batches.some(b => b.daysLeft <= 0);
            const nearExpiry = batches.some(b => b.daysLeft > 0 && b.daysLeft <= 7);
            
            if (hasExpired) {
                expiryCell.innerHTML = `
                    <div class="alert alert-danger py-1 mb-1">
                        <i class="fas fa-exclamation-circle me-1"></i> Expired batch present
                    </div>
                    ${batches.map(batch => `
                        <div class="expiry-item ${batch.daysLeft <= 0 ? 'text-danger' : batch.daysLeft <= 7 ? 'text-warning' : ''}">
                            <small>${batch.daysLeft <= 0 ? 'Expired' : batch.daysLeft + ' days left'}</small>
                            <div class="progress mt-1" style="height: 4px;">
                                <div class="progress-bar ${
                                    batch.daysLeft <= 0 ? 'bg-danger' : 
                                    batch.daysLeft <= 7 ? 'bg-warning' : 
                                    batch.daysLeft <= 30 ? 'bg-info' : 'bg-success'
                                }" 
                                style="width: ${Math.min(100, Math.max(0, batch.daysLeft) * 3)}%"></div>
                            </div>
                        </div>
                    `).join('')}
                `;
            } else if (nearExpiry) {
                expiryCell.innerHTML = `
                    <div class="alert alert-warning py-1 mb-1">
                        <i class="fas fa-exclamation-triangle me-1"></i> Near expiry
                    </div>
                    ${batches.map(batch => `
                        <div class="expiry-item ${batch.daysLeft <= 7 ? 'text-warning' : ''}">
                            <small>${batch.daysLeft} days left</small>
                            <div class="progress mt-1" style="height: 4px;">
                                <div class="progress-bar ${
                                    batch.daysLeft <= 7 ? 'bg-warning' : 
                                    batch.daysLeft <= 30 ? 'bg-info' : 'bg-success'
                                }" 
                                style="width: ${Math.min(100, batch.daysLeft * 3)}%"></div>
                            </div>
                        </div>
                    `).join('')}
                `;
            } else {
                expiryCell.innerHTML = `
                    <div class="alert alert-success py-1 mb-1">
                        <i class="fas fa-check-circle me-1"></i> Good condition
                    </div>
                    ${batches.map(batch => `
                        <div class="expiry-item">
                            <small>${batch.daysLeft} days left</small>
                            <div class="progress mt-1" style="height: 4px;">
                                <div class="progress-bar ${
                                    batch.daysLeft <= 30 ? 'bg-info' : 'bg-success'
                                }" 
                                style="width: ${Math.min(100, batch.daysLeft)}%"></div>
                            </div>
                        </div>
                    `).join('')}
                `;
            }
            
            row.appendChild(expiryCell);
            
            // Add action cell
            const actionCell = document.createElement('td');
            if (hasExpired) {
                actionCell.innerHTML = `
                    <button class="btn btn-sm btn-danger mb-1" onclick="alert('Marked ${batches.filter(b => b.daysLeft <= 0).reduce((sum, b) => sum + b.quantity, 0)} units for disposal')">
                        <i class="fas fa-trash-alt me-1"></i> Dispose
                    </button>
                    <button class="btn btn-sm btn-outline-primary mt-1" onclick="alert('FIFO enforcement activated for ${item.name}')">
                        <i class="fas fa-sort-amount-down me-1"></i> FIFO
                    </button>
                `;
            } else if (nearExpiry) {
                actionCell.innerHTML = `
                    <button class="btn btn-sm btn-warning mb-1" onclick="alert('Marked ${batches.filter(b => b.daysLeft <= 7).reduce((sum, b) => sum + b.quantity, 0)} units for promotion')">
                        <i class="fas fa-tag me-1"></i> Discount
                    </button>
                    <button class="btn btn-sm btn-outline-primary mt-1" onclick="alert('FIFO enforcement activated for ${item.name}')">
                        <i class="fas fa-sort-amount-down me-1"></i> FIFO
                    </button>
                `;
            } else {
                actionCell.innerHTML = `
                    <button class="btn btn-sm btn-outline-primary" onclick="alert('FIFO enforcement activated for ${item.name}')">
                        <i class="fas fa-sort-amount-down me-1"></i> FIFO
                    </button>
                `;
            }
            
            row.appendChild(actionCell);
        });

        console.log("Expiry tracking applied successfully");
    } catch (error) {
        console.error("Error in expiry tracking:", error);
        showErrorNotification("Error applying expiry tracking: " + error.message);
    }
}

// Apply sales analytics simulation
function applySalesAnalytics(items) {
    console.log("Starting sales analytics for", items.length, "items");
    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    // Create a simulation info row
    const infoRow = document.createElement('tr');
    infoRow.classList.add('simulation-info-row');
    infoRow.innerHTML = `
        <td colspan="12" class="p-3 bg-info text-white">
            <i class="fas fa-chart-bar me-2"></i>
            <strong>Sales Analytics:</strong> Detailed performance metrics with seasonal pattern analysis.
            <button class="btn btn-sm btn-light ms-3" onclick="loadInventoryData()">Reset</button>
        </td>
    `;
    
    // Insert at the top of the table
    tableBody.insertBefore(infoRow, tableBody.firstChild);
    
    try {
        // Update table headers for sales analytics
        const headerRow = document.querySelector('#inventoryTable thead tr');
        if (headerRow) {
            // Clear the existing header cells except for the first 9
            const headerCells = headerRow.querySelectorAll('th');
            for (let i = headerCells.length - 1; i >= 9; i--) {
                if (headerCells[i]) {
                    headerCells[i].remove();
                }
            }
            
            // Add new header cells
            const salesTrendHeader = document.createElement('th');
            salesTrendHeader.textContent = 'Sales Trend';
            headerRow.appendChild(salesTrendHeader);
            
            const seasonalHeader = document.createElement('th');
            seasonalHeader.textContent = 'Seasonal Pattern';
            headerRow.appendChild(seasonalHeader);
            
            const actionHeader = document.createElement('th');
            actionHeader.textContent = 'Action';
            headerRow.appendChild(actionHeader);
        }
        
        // Add sales analytics to each item
        items.forEach(item => {
            const row = document.querySelector(`tr[data-id="${item.id}"]`);
            if (!row) return;
            
            // Generate simulated sales data
            const salesChange = (Math.random() * 40 - 20).toFixed(1); // -20% to +20%
            const salesTrend = salesChange > 10 ? 'Strong Growth' : 
                            salesChange > 0 ? 'Moderate Growth' :
                            salesChange > -10 ? 'Slight Decline' : 'Sharp Decline';
            
            // Generate seasonal pattern based on product category
            let seasonalPattern, peakMonths;
            
            if (item.category === 'Confectionery') {
                seasonalPattern = 'Holiday-driven';
                peakMonths = 'Oct-Dec';
            } else if (item.category === 'Dairy') {
                seasonalPattern = 'Consistent';
                peakMonths = 'Year-round';
            } else if (item.category === 'Essentials') {
                seasonalPattern = 'Consistent';
                peakMonths = 'Year-round';
            } else {
                seasonalPattern = 'Seasonal';
                peakMonths = 'Jun-Aug';
            }
            
            // Make sure we have at least the minimum number of cells
            while (row.cells.length < 9) {
                row.appendChild(document.createElement('td'));
            }
            
            // Remove any cells beyond the 9th one (we'll add our 3 new ones)
            while (row.cells.length > 9) {
                row.deleteCell(row.cells.length - 1);
            }
            
            // Add sales trend cell
            const trendCell = document.createElement('td');
            trendCell.innerHTML = `
                <div class="sales-trend">
                    <span class="trend-badge badge ${salesChange > 0 ? 'bg-success' : 'bg-danger'}">
                        ${salesChange > 0 ? '+' : ''}${salesChange}%
                    </span>
                    <div class="trend-label mt-1">${salesTrend}</div>
                    <div class="trend-chart mt-2">
                        ${generateMiniChart(salesChange)}
                    </div>
                </div>
            `;
            row.appendChild(trendCell);
            
            // Add seasonal pattern cell
            const seasonalCell = document.createElement('td');
            seasonalCell.innerHTML = `
                <div class="seasonal-pattern">
                    <div class="pattern-type mb-1">${seasonalPattern}</div>
                    <div class="peak-months mb-1">
                        <small class="text-muted">Peak: ${peakMonths}</small>
                    </div>
                    <div class="year-chart">
                        ${generateSeasonalChart(seasonalPattern)}
                    </div>
                </div>
            `;
            row.appendChild(seasonalCell);
            
            // Add action cell
            const actionCell = document.createElement('td');
            
            if (salesChange < -10) {
                actionCell.innerHTML = `
                    <button class="btn btn-sm btn-danger mb-1" onclick="alert('Markdown strategy created for ${item.name}')">
                        <i class="fas fa-arrow-down me-1"></i> Markdown
                    </button>
                    <button class="btn btn-sm btn-outline-secondary mt-1" onclick="alert('Detailed report generated for ${item.name}')">
                        <i class="fas fa-file-alt me-1"></i> Report
                    </button>
                `;
            } else if (salesChange > 10) {
                actionCell.innerHTML = `
                    <button class="btn btn-sm btn-success mb-1" onclick="alert('Stock increase plan created for ${item.name}')">
                        <i class="fas fa-arrow-up me-1"></i> Increase Stock
                    </button>
                    <button class="btn btn-sm btn-outline-secondary mt-1" onclick="alert('Detailed report generated for ${item.name}')">
                        <i class="fas fa-file-alt me-1"></i> Report
                    </button>
                `;
            } else {
                actionCell.innerHTML = `
                    <button class="btn btn-sm btn-info mb-1" onclick="alert('Stock optimization plan created for ${item.name}')">
                        <i class="fas fa-balance-scale me-1"></i> Optimize
                    </button>
                    <button class="btn btn-sm btn-outline-secondary mt-1" onclick="alert('Detailed report generated for ${item.name}')">
                        <i class="fas fa-file-alt me-1"></i> Report
                    </button>
                `;
            }
            
            row.appendChild(actionCell);
        });

        console.log("Sales analytics applied successfully");
    } catch (error) {
        console.error("Error in sales analytics:", error);
        showErrorNotification("Error applying sales analytics: " + error.message);
    }
}

// Generate mini chart for sales trend
function generateMiniChart(salesChange) {
    // Simple mini bar chart with 6 bars
    const barCount = 6;
    let bars = '';
    
    for (let i = 0; i < barCount; i++) {
        // For the trend, make each bar in relation to the sales change
        // Last bar should be the current change
        const baseHeight = 30; // base height in pixels
        let height;
        
        if (i === barCount - 1) {
            // Current value (sales change)
            height = baseHeight + (parseFloat(salesChange) * 1.5);
        } else {
            // Previous values (random but trending toward current)
            const factor = i / (barCount - 1); // 0 to 1
            const randomVariation = (Math.random() * 20) - 10; // -10 to +10
            height = baseHeight + (factor * parseFloat(salesChange) * 1.5) + randomVariation;
        }
        
        // Ensure minimum height
        height = Math.max(5, height);
        
        const barClass = i === barCount - 1 ? 
            (parseFloat(salesChange) > 0 ? 'trend-bar-current-up' : 'trend-bar-current-down') : 
            'trend-bar';
        
        bars += `<div class="${barClass}" style="height: ${height}px;"></div>`;
    }
    
    return `<div class="mini-chart">${bars}</div>`;
}

// Generate seasonal chart
function generateSeasonalChart(pattern) {
    // Simple yearly line chart showing 12 months
    const months = 12;
    let dots = '';
    
    const baseHeight = 15; // base height in pixels
    const maxVariation = 15; // maximum height variation
    
    for (let i = 0; i < months; i++) {
        let height;
        
        if (pattern === 'Holiday-driven') {
            // Higher in Oct-Dec (9-11)
            if (i >= 9) {
                height = baseHeight + maxVariation - (Math.random() * 5);
            } else {
                height = baseHeight + (Math.random() * 8) - 4;
            }
        } else if (pattern === 'Seasonal' && i >= 5 && i <= 7) {
            // Higher in Jun-Aug (5-7)
            height = baseHeight + maxVariation - (Math.random() * 5);
        } else if (pattern === 'Consistent') {
            // Consistent with small variations
            height = baseHeight + (Math.random() * 6) - 3;
        } else {
            // Other patterns - random variations
            height = baseHeight + (Math.random() * 10) - 5;
        }
        
        // Ensure minimum height
        height = Math.max(5, height);
        
        // Highlight peak months
        const isPeak = (pattern === 'Holiday-driven' && i >= 9) || 
                       (pattern === 'Seasonal' && i >= 5 && i <= 7);
        
        const dotClass = isPeak ? 'season-dot-peak' : 'season-dot';
        
        dots += `<div class="${dotClass}" style="bottom: ${height}px;"></div>`;
    }
    
    return `<div class="season-chart">${dots}</div>`;
}

// Apply inventory restructuring simulation
function applyInventoryRestructuring(items) {
    const tableBody = document.getElementById('inventoryTableBody');
    if (!tableBody) return;
    
    // Create a simulation info row
    const infoRow = document.createElement('tr');
    infoRow.classList.add('simulation-info-row');
    infoRow.innerHTML = `
        <td colspan="12" class="p-3 bg-secondary text-white">
            <i class="fas fa-layer-group me-2"></i>
            <strong>Inventory Restructuring:</strong> FIFO/LIFO implementation with product hierarchies.
            <button class="btn btn-sm btn-light ms-3" onclick="loadInventoryData()">Reset</button>
        </td>
    `;
    
    // Insert at the top of the table
    tableBody.insertBefore(infoRow, tableBody.firstChild);
    
    // Group items by category to create hierarchy
    const categories = {};
    items.forEach(item => {
        if (!categories[item.category]) {
            categories[item.category] = [];
        }
        categories[item.category].push(item);
    });
    
    // Clear the table body except for the info row
    const infoRows = tableBody.querySelectorAll('.simulation-info-row');
    tableBody.innerHTML = '';
    infoRows.forEach(row => tableBody.appendChild(row));
    
    // Update table headers
    const headerRow = document.querySelector('#inventoryTable thead tr');
    if (headerRow) {
        headerRow.innerHTML = `
            <th>Category/Product</th>
            <th>SKU</th>
            <th>Quantity</th>
            <th>Value</th>
            <th>Method</th>
            <th>Valuation</th>
            <th>Actions</th>
        `;
    }
    
    // Add category groups and products
    Object.keys(categories).sort().forEach(category => {
        // Add category row
        const categoryRow = document.createElement('tr');
        categoryRow.classList.add('category-row');
        
        const categoryItems = categories[category];
        const totalCategoryValue = categoryItems.reduce((sum, item) => 
            sum + (item.quantity * item.cost), 0);
        
        categoryRow.innerHTML = `
            <td colspan="7" class="category-header">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <i class="fas fa-folder me-2"></i>
                        <strong>${category}</strong>
                        <span class="badge bg-primary ms-2">${categoryItems.length} Products</span>
                    </div>
                    <div>
                        <span class="badge bg-success">₹${totalCategoryValue.toLocaleString('en-IN')}</span>
                    </div>
                </div>
            </td>
        `;
        
        tableBody.appendChild(categoryRow);
        
        // Add product rows for this category
        categoryItems.forEach(item => {
            // Determine valuation method (random for simulation)
            const methods = ['FIFO', 'LIFO', 'WAC']; // First-In-First-Out, Last-In-First-Out, Weighted Average Cost
            const method = methods[Math.floor(Math.random() * methods.length)];
            
            // Calculate inventory value
            const totalValue = item.quantity * item.cost;
            
            // Generate FIFO/LIFO value variation (simulation)
            let methodValue = totalValue;
            let valueDifference = 0;
            
            if (method === 'FIFO') {
                // FIFO typically results in lower COGS in inflationary environments
                methodValue = totalValue * (1 - (Math.random() * 0.05));
                valueDifference = totalValue - methodValue;
            } else if (method === 'LIFO') {
                // LIFO typically results in higher COGS in inflationary environments
                methodValue = totalValue * (1 + (Math.random() * 0.06));
                valueDifference = methodValue - totalValue;
            }
            
            // Create product row
            const productRow = document.createElement('tr');
            productRow.dataset.id = item.id;
            productRow.classList.add('product-row');
            
            productRow.innerHTML = `
                <td>
                    <div class="ps-4">
                        <i class="fas fa-box me-2"></i>
                        ${item.name}
                    </div>
                </td>
                <td>${item.sku}</td>
                <td>${item.quantity}</td>
                <td>₹${totalValue.toLocaleString('en-IN')}</td>
                <td>
                    <select class="form-select form-select-sm inventory-method">
                        ${methods.map(m => `<option value="${m}" ${m === method ? 'selected' : ''}>${m}</option>`).join('')}
                    </select>
                </td>
                <td>
                    <div>₹${methodValue.toLocaleString('en-IN')}</div>
                    <small class="${valueDifference >= 0 ? 'text-success' : 'text-danger'}">
                        ${valueDifference >= 0 ? '+' : ''}₹${Math.abs(valueDifference).toLocaleString('en-IN')}
                    </small>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="alert('Hierarchy editor opened for ${item.name}')">
                        <i class="fas fa-sitemap"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="alert('Taxonomy updated for ${item.name}')">
                        <i class="fas fa-tag"></i>
                    </button>
                </td>
            `;
            
            tableBody.appendChild(productRow);
        });
    });
    
    // Add listener for method change
    document.querySelectorAll('.inventory-method').forEach(select => {
        select.addEventListener('change', function() {
            const row = this.closest('tr');
            const valueCell = row.cells[5];
            const currentValue = parseFloat(valueCell.textContent.replace(/[₹,]/g, ''));
            
            // Simulate value change based on selected method
            let newValue, valueDifference;
            
            if (this.value === 'FIFO') {
                newValue = currentValue * (1 - (Math.random() * 0.05));
                valueDifference = currentValue - newValue;
            } else if (this.value === 'LIFO') {
                newValue = currentValue * (1 + (Math.random() * 0.06));
                valueDifference = newValue - currentValue;
            } else {
                // WAC - somewhere in between
                newValue = currentValue * (1 + (Math.random() * 0.02 - 0.01));
                valueDifference = newValue - currentValue;
            }
            
            valueCell.innerHTML = `
                <div>₹${newValue.toLocaleString('en-IN')}</div>
                <small class="${valueDifference >= 0 ? 'text-success' : 'text-danger'}">
                    ${valueDifference >= 0 ? '+' : ''}₹${Math.abs(valueDifference).toLocaleString('en-IN')}
                </small>
            `;

            // Show notification of the change
            showSuccessNotification(`Valuation method updated to ${this.value}`);
        });
    });
}

// Show processing notification
function showProcessingNotification(message = 'Processing...') {
    const notification = document.createElement('div');
    notification.classList.add('processing-notification');
    notification.innerHTML = `
        <div class="spinner-border spinner-border-sm text-light me-2"></div>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Show success notification
function showSuccessNotification(message = 'Success') {
    const notification = document.createElement('div');
    notification.classList.add('success-notification');
    notification.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Show error notification
function showErrorNotification(message = 'Error occurred') {
    const notification = document.createElement('div');
    notification.classList.add('error-notification');
    notification.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Item edit functionality
function editItem(id) {
    alert(`Edit functionality for item ID: ${id}`);
}

// Item order functionality
function orderItem(id) {
    alert(`Order functionality for item ID: ${id}`);
}

// Process product image with Gemini API
function processProductImage(file, base64Image) {
    // Show processing notification
    const notification = showProcessingNotification('Analyzing product image...');
   
    // Extract base64 data (remove prefix)
    const base64Data = base64Image.replace(/^data:image\/(png|jpeg|jpg);base64,/, '');
   
    // Send to backend
    fetch('/api/product/process-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image_data: base64Data
        })
    })
        .then(response => response.json())
        .then(data => {
            // Remove processing notification
            notification.remove();
           
            if (data.status === 'success') {
                // Show modal for product details
                const productModal = new bootstrap.Modal(document.getElementById('productModal'));
               
                // Set image in modal
                const modalProductImage = document.getElementById('modalProductImage');
                if (modalProductImage) {
                    modalProductImage.src = base64Image;
                }
               
                // Pre-fill form fields with recognized data
                if (data.product) {
                    document.getElementById('productName').value = data.product.name || '';
                    document.getElementById('productBrand').value = data.product.brand || '';
                    document.getElementById('productCategory').value = data.product.category || '';
                    document.getElementById('productSku').value = data.product.sku || generateSku();
                    document.getElementById('productQuantity').value = '10'; // Default
                    document.getElementById('productPrice').value = data.product.price || '';
                    document.getElementById('productCostPrice').value = data.product.cost_price || '';
                    document.getElementById('productReorderLevel').value = '5'; // Default
                }
               
                productModal.show();
               
                // Setup form submission
                document.getElementById('productForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    addProductFromForm();
                });
               
                showSuccessNotification('Product image analyzed successfully');
            } else {
                showErrorNotification(data.message || 'Error analyzing product image');
            }
        })
        .catch(error => {
            // Remove processing notification
            notification.remove();
           
            console.error('Error:', error);
            showErrorNotification('Error processing product image');
        });
}
 
// Generate SKU
function generateSku() {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const prefix = characters.charAt(Math.floor(Math.random() * characters.length)) +
                 characters.charAt(Math.floor(Math.random() * characters.length));
    const suffix = Math.floor(1000 + Math.random() * 9000);
    return prefix + suffix;
}
 
// Add product from form
function addProductFromForm() {
    // Get form values
    const product = {
        name: document.getElementById('productName').value,
        brand: document.getElementById('productBrand').value,
        category: document.getElementById('productCategory').value,
        sku: document.getElementById('productSKU').value,
        quantity: parseInt(document.getElementById('productQuantity').value),
        price: parseFloat(document.getElementById('productPrice').value),
        cost_price: parseFloat(document.getElementById('productCostPrice').value),
        reorder_level: parseInt(document.getElementById('productReorderLevel').value)
    };
   
    // Show processing notification
    const notification = showProcessingNotification('Adding product to inventory...');
   
    // Send to backend
    fetch('/api/inventory/add-product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(product)
    })
        .then(response => response.json())
        .then(data => {
            // Remove processing notification
            notification.remove();
           
            if (data.status === 'success') {
                // Close the modal
                const productModal = bootstrap.Modal.getInstance(document.getElementById('productDetailsModal'));
                if (productModal) {
                    productModal.hide();
                }
               
                // Clear the form
                document.getElementById('productForm').reset();
               
                // Clear the image preview
                const removeBarcodeBtn = document.getElementById('removeBarcodeBtn');
                if (removeBarcodeBtn) {
                    removeBarcodeBtn.click();
                }
               
                showSuccessNotification('Product added successfully');
                
                // Wait a bit before reloading to prevent UI conflicts
                setTimeout(() => {
                    loadInventoryData(); // Reload data
                    updateInventoryStats(); // Update the stats display
                }, 300);
            } else {
                showErrorNotification(data.message || 'Error adding product');
            }
        })
        .catch(error => {
            // Remove processing notification
            if (notification && notification.parentNode) {
                notification.remove();
            }
           
            console.error('Error:', error);
            showErrorNotification('Error adding product: ' + (error.message || 'Unknown error'));
        });
}
 
// Display processing notification
function showProcessingNotification(message = 'Processing...') {
    const notification = document.createElement('div');
    notification.className = 'processing-notification';
    notification.innerHTML = `
        <div class="spinner">
            <i class="fas fa-circle-notch fa-spin"></i>
        </div>
        <div class="message">${message}</div>
    `;
   
    document.body.appendChild(notification);
    return notification;
}
 
// Display success notification
function showSuccessNotification(message = 'Success') {
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
   
    document.body.appendChild(notification);
   
    setTimeout(() => {
        notification.classList.add('show');
       
        setTimeout(() => {
            notification.classList.remove('show');
           
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }, 100);
}
 
// Display error notification
function showErrorNotification(message = 'Error occurred') {
    const notification = document.createElement('div');
    notification.className = 'notification error';
    notification.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
   
    document.body.appendChild(notification);
   
    setTimeout(() => {
        notification.classList.add('show');
       
        setTimeout(() => {
            notification.classList.remove('show');
           
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }, 100);
}
 
// Edit an item
function editItem(id) {
    // Implement edit functionality
    alert(`Edit item with ID: ${id} - This functionality is not implemented yet.`);
}
 
// Order an item
function orderItem(id) {
    // Implement order functionality
    alert(`Order item with ID: ${id} - This functionality is not implemented yet.`);
}


