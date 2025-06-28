document.addEventListener('DOMContentLoaded', function() {
    // Initialize navigation
    initializeNavigation();
    
    // Load initial data
    loadStores();
    loadCurrencies();
    loadProducts();
    loadCustomers();
    loadDistributors();
    loadOrders();
    loadConfig();
    
    // Add event listeners for store management
    document.getElementById('saveStore')?.addEventListener('click', handleSaveStore);
    document.getElementById('saveCurrency')?.addEventListener('click', handleSaveCurrency);
    document.getElementById('saveProduct')?.addEventListener('click', handleSaveProduct);
    document.getElementById('saveCustomer')?.addEventListener('click', handleSaveCustomer);
    document.getElementById('saveDistributor')?.addEventListener('click', handleSaveDistributor);
    document.getElementById('saveCustomerOrder')?.addEventListener('click', handleSaveCustomerOrder);
    document.getElementById('saveDistributorOrder')?.addEventListener('click', handleSaveDistributorOrder);
    document.getElementById('saveConfig')?.addEventListener('click', handleSaveConfig);
    
    // Add event listeners for import/export
    document.getElementById('importProducts')?.addEventListener('click', () => {
        document.getElementById('importProductsModal').modal('show');
    });
    document.getElementById('exportProducts')?.addEventListener('click', exportProducts);
    
    // Add event listeners for API key toggle
    document.getElementById('toggleApiKey')?.addEventListener('click', toggleApiKeyVisibility);
});

// Initialize navigation
function initializeNavigation() {
    const links = document.querySelectorAll('#sidebar .nav-link');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            links.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding tab content
            const target = document.querySelector(this.getAttribute('href'));
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            target.classList.add('show', 'active');
        });
    });
}

// Load stores data
function loadStores() {
    fetch('/api/stores')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateStoresTable(data.stores);
                updateStoreCards(data.stores);
            } else {
                showAlert('danger', data.message || 'Failed to load stores');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Failed to load stores');
        });
}

// Update stores table
function updateStoresTable(stores) {
    const tbody = document.getElementById('storesTableBody');
    tbody.innerHTML = '';
    
    stores.forEach(store => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${store.store_name}</td>
            <td>
                <span class="flag-icon flag-icon-${store.country_code.toLowerCase()}"></span>
                ${store.country_name}
            </td>
            <td>${store.currency_symbol}</td>
            <td>
                <span class="badge ${store.is_active ? 'bg-success' : 'bg-secondary'}">
                    ${store.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary edit-store" data-store-id="${store.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-store" data-store-id="${store.id}">
                    <i class="fas fa-trash"></i>
                </button>
                ${!store.is_active ? `
                    <button class="btn btn-sm btn-outline-success activate-store" data-store-id="${store.id}">
                        <i class="fas fa-check"></i>
                    </button>
                ` : ''}
            </td>
        `;
        
        // Add event listeners for the buttons
        tr.querySelector('.edit-store')?.addEventListener('click', () => editStore(store.id));
        tr.querySelector('.delete-store')?.addEventListener('click', () => deleteStore(store.id));
        tr.querySelector('.activate-store')?.addEventListener('click', () => activateStore(store.id));
        
        tbody.appendChild(tr);
    });
}

function updateStoreCards(stores) {
    const container = document.getElementById('storeCards');
    container.innerHTML = '';
    
    stores.forEach(store => {
        const col = document.createElement('div');
        col.className = 'col';
        col.innerHTML = `
            <div class="card h-100 store-card ${store.is_active ? 'border-primary' : ''}" 
                 onclick="selectStore('${store.country_code}')" style="cursor: pointer;">
                <img src="/static/images/avatar-${store.country_code.toLowerCase()}.png" 
                     class="card-img-top p-3" alt="${store.country_name} Store"
                     style="height: 200px; object-fit: contain;">
                <div class="card-body text-center">
                    <h5 class="card-title">${store.store_name}</h5>
                    <p class="card-text">
                        <span class="flag-icon flag-icon-${store.country_code.toLowerCase()}"></span>
                        ${store.currency_symbol} (${store.currency_code})
                    </p>
                    ${store.is_active ? '<span class="badge bg-primary">Active</span>' : ''}
                </div>
            </div>
        `;
        container.appendChild(col);
    });
}

// Handle save store
function handleSaveStore() {
    const storeName = document.getElementById('storeName').value;
    const countryCode = document.getElementById('countryCode').value;
    const currencyCode = document.getElementById('currencyCode').value;
    
    if (!storeName || !countryCode || !currencyCode) {
        showAlert('danger', 'Please fill in all required fields');
        return;
    }
    
    const storeData = {
        store_name: storeName,
        country_code: countryCode,
        currency_code: currencyCode
    };
    
    const storeId = document.getElementById('storeId').value;
    const method = storeId ? 'PUT' : 'POST';
    const url = storeId ? `/api/stores/${storeId}` : '/api/stores';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(storeData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', `Store ${storeId ? 'updated' : 'added'} successfully`);
            loadStores();
            bootstrap.Modal.getInstance(document.getElementById('addStoreModal')).hide();
            document.getElementById('storeForm').reset();
        } else {
            showAlert('danger', data.message || `Failed to ${storeId ? 'update' : 'add'} store`);
        }
    })
    .catch(error => {
        console.error('Error saving store:', error);
        showAlert('danger', `Failed to ${storeId ? 'update' : 'add'} store`);
    });
}

// Load currencies data
function loadCurrencies() {
    fetch('/api/currencies')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateCurrenciesTable(data.currencies);
                updateCurrencySelects(data.currencies);
            } else {
                showAlert('error', 'Failed to load currencies');
            }
        })
        .catch(error => {
            console.error('Error loading currencies:', error);
            showAlert('error', 'Failed to load currencies');
        });
}

// Update currencies table
function updateCurrenciesTable(currencies) {
    const tbody = document.getElementById('currenciesTableBody');
    tbody.innerHTML = '';
    
    currencies.forEach(currency => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${currency.code}</td>
            <td>${currency.name}</td>
            <td>${currency.symbol}</td>
            <td>${currency.exchange_rate}</td>
            <td>${currency.updated_at ? new Date(currency.updated_at).toLocaleString() : 'Never'}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary edit-currency" data-currency-id="${currency.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-currency" data-currency-id="${currency.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    // Add event listeners for currency actions
    document.querySelectorAll('.edit-currency').forEach(btn => {
        btn.addEventListener('click', () => editCurrency(btn.dataset.currencyId));
    });
    document.querySelectorAll('.delete-currency').forEach(btn => {
        btn.addEventListener('click', () => deleteCurrency(btn.dataset.currencyId));
    });
}

// Update currency selects
function updateCurrencySelects(currencies) {
    const selects = document.querySelectorAll('select[data-type="currency"]');
    selects.forEach(select => {
        select.innerHTML = '<option value="">Select Currency</option>';
        currencies.forEach(currency => {
            select.innerHTML += `
                <option value="${currency.code}">${currency.name} (${currency.symbol})</option>
            `;
        });
    });
}

// Handle save currency
function handleSaveCurrency() {
    const currencyCode = document.getElementById('currencyCode').value;
    const currencyName = document.getElementById('currencyName').value;
    const currencySymbol = document.getElementById('currencySymbol').value;
    const exchangeRate = document.getElementById('exchangeRate').value;
    
    if (!currencyCode || !currencyName || !currencySymbol || !exchangeRate) {
        showAlert('error', 'Please fill in all required fields');
        return;
    }
    
    const currencyData = {
        code: currencyCode,
        name: currencyName,
        symbol: currencySymbol,
        exchange_rate: parseFloat(exchangeRate)
    };
    
    const currencyId = document.getElementById('saveCurrency').dataset.currencyId;
    const method = currencyId ? 'PUT' : 'POST';
    const url = currencyId ? `/api/currencies/${currencyId}` : '/api/currencies';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(currencyData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', `Currency ${currencyId ? 'updated' : 'added'} successfully`);
            loadCurrencies();
            bootstrap.Modal.getInstance(document.getElementById('addCurrencyModal')).hide();
            document.getElementById('currencyForm').reset();
        } else {
            showAlert('error', data.message || `Failed to ${currencyId ? 'update' : 'add'} currency`);
        }
    })
    .catch(error => {
        console.error('Error saving currency:', error);
        showAlert('error', `Failed to ${currencyId ? 'update' : 'add'} currency`);
    });
}

// Load products data
function loadProducts() {
    fetch('/api/products')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateProductsTable(data.products);
            } else {
                showAlert('error', 'Failed to load products');
            }
        })
        .catch(error => {
            console.error('Error loading products:', error);
            showAlert('error', 'Failed to load products');
        });
}

// Update products table
function updateProductsTable(products) {
    const tbody = document.getElementById('productsTableBody');
    tbody.innerHTML = '';
    
    products.forEach(product => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${product.sku}</td>
            <td>${product.name}</td>
            <td>${product.category}</td>
            <td>${formatCurrency(product.price)}</td>
            <td>${formatCurrency(product.cost_price)}</td>
            <td>${product.quantity}</td>
            <td>
                <span class="badge ${product.is_active ? 'bg-success' : 'bg-secondary'}">
                    ${product.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary edit-product" data-product-id="${product.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-product" data-product-id="${product.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    // Add event listeners for product actions
    document.querySelectorAll('.edit-product').forEach(btn => {
        btn.addEventListener('click', () => editProduct(btn.dataset.productId));
    });
    document.querySelectorAll('.delete-product').forEach(btn => {
        btn.addEventListener('click', () => deleteProduct(btn.dataset.productId));
    });
}

// Handle save product
function handleSaveProduct() {
    const productData = {
        sku: document.getElementById('productSku').value,
        name: document.getElementById('productName').value,
        category: document.getElementById('productCategory').value,
        description: document.getElementById('productDescription').value,
        price: parseFloat(document.getElementById('price').value),
        cost_price: parseFloat(document.getElementById('costPrice').value),
        quantity: parseInt(document.getElementById('quantity').value),
        is_active: document.getElementById('isActive').checked
    };
    
    if (!productData.sku || !productData.name || !productData.category || 
        isNaN(productData.price) || isNaN(productData.cost_price) || isNaN(productData.quantity)) {
        showAlert('error', 'Please fill in all required fields');
        return;
    }
    
    const productId = document.getElementById('saveProduct').dataset.productId;
    const method = productId ? 'PUT' : 'POST';
    const url = productId ? `/api/products/${productId}` : '/api/products';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(productData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', `Product ${productId ? 'updated' : 'added'} successfully`);
            loadProducts();
            bootstrap.Modal.getInstance(document.getElementById('addProductModal')).hide();
            document.getElementById('productForm').reset();
        } else {
            showAlert('error', data.message || `Failed to ${productId ? 'update' : 'add'} product`);
        }
    })
    .catch(error => {
        console.error('Error saving product:', error);
        showAlert('error', `Failed to ${productId ? 'update' : 'add'} product`);
    });
}

// Load customers data
function loadCustomers() {
    fetch('/api/customers')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateCustomersTable(data.customers);
            } else {
                showAlert('error', 'Failed to load customers');
            }
        })
        .catch(error => {
            console.error('Error loading customers:', error);
            showAlert('error', 'Failed to load customers');
        });
}

// Update customers table
function updateCustomersTable(customers) {
    const tbody = document.getElementById('customersTableBody');
    tbody.innerHTML = '';
    
    customers.forEach(customer => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${customer.id}</td>
            <td>${customer.name}</td>
            <td>${customer.email}</td>
            <td>${customer.phone || '-'}</td>
            <td>${customer.address || '-'}</td>
            <td>
                <span class="badge ${customer.is_active ? 'bg-success' : 'bg-secondary'}">
                    ${customer.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary edit-customer" data-customer-id="${customer.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-customer" data-customer-id="${customer.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    // Add event listeners for customer actions
    document.querySelectorAll('.edit-customer').forEach(btn => {
        btn.addEventListener('click', () => editCustomer(btn.dataset.customerId));
    });
    document.querySelectorAll('.delete-customer').forEach(btn => {
        btn.addEventListener('click', () => deleteCustomer(btn.dataset.customerId));
    });
}

// Handle save customer
function handleSaveCustomer() {
    const customerData = {
        name: document.getElementById('customerName').value,
        email: document.getElementById('customerEmail').value,
        phone: document.getElementById('customerPhone').value,
        address: document.getElementById('customerAddress').value,
        is_active: document.getElementById('customerIsActive').checked
    };
    
    if (!customerData.name || !customerData.email) {
        showAlert('error', 'Please fill in all required fields');
        return;
    }
    
    const customerId = document.getElementById('saveCustomer').dataset.customerId;
    const method = customerId ? 'PUT' : 'POST';
    const url = customerId ? `/api/customers/${customerId}` : '/api/customers';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(customerData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', `Customer ${customerId ? 'updated' : 'added'} successfully`);
            loadCustomers();
            bootstrap.Modal.getInstance(document.getElementById('addCustomerModal')).hide();
            document.getElementById('customerForm').reset();
        } else {
            showAlert('error', data.message || `Failed to ${customerId ? 'update' : 'add'} customer`);
        }
    })
    .catch(error => {
        console.error('Error saving customer:', error);
        showAlert('error', `Failed to ${customerId ? 'update' : 'add'} customer`);
    });
}

// Load distributors data
function loadDistributors() {
    fetch('/api/distributors')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateDistributorsTable(data.distributors);
            } else {
                showAlert('error', 'Failed to load distributors');
            }
        })
        .catch(error => {
            console.error('Error loading distributors:', error);
            showAlert('error', 'Failed to load distributors');
        });
}

// Update distributors table
function updateDistributorsTable(distributors) {
    const tbody = document.getElementById('distributorsTableBody');
    tbody.innerHTML = '';
    
    distributors.forEach(distributor => {
        tbody.innerHTML += `
            <tr>
                <td>${distributor.id}</td>
                <td>${distributor.name}</td>
                <td>${distributor.email}</td>
                <td>${distributor.phone || '-'}</td>
                <td>${distributor.address || '-'}</td>
                <td><span class="badge ${distributor.is_active ? 'bg-success' : 'bg-secondary'}">${distributor.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary edit-distributor" data-distributor-id="${distributor.id}"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger delete-distributor" data-distributor-id="${distributor.id}"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    });
    // Add event listeners for distributor actions
    document.querySelectorAll('.edit-distributor').forEach(btn => {
        btn.addEventListener('click', () => editDistributor(btn.dataset.distributorId));
    });
    document.querySelectorAll('.delete-distributor').forEach(btn => {
        btn.addEventListener('click', () => deleteDistributor(btn.dataset.distributorId));
    });
}

// Handle save distributor
function handleSaveDistributor() {
    const distributorData = {
        name: document.getElementById('distributorName').value,
        email: document.getElementById('distributorEmail').value,
        phone: document.getElementById('distributorPhone').value,
        address: document.getElementById('distributorAddress').value,
        is_active: document.getElementById('distributorIsActive').checked
    };
    if (!distributorData.name || !distributorData.email) {
        showAlert('error', 'Name and email are required');
        return;
    }
    const distributorId = document.getElementById('saveDistributor').dataset.distributorId;
    const method = distributorId ? 'PUT' : 'POST';
    const url = distributorId ? `/api/distributors/${distributorId}` : '/api/distributors';
    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(distributorData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showAlert('success', `Distributor ${distributorId ? 'updated' : 'added'} successfully`);
                loadDistributors();
                bootstrap.Modal.getInstance(document.getElementById('addDistributorModal')).hide();
                document.getElementById('distributorForm').reset();
            } else {
                showAlert('error', data.message || `Failed to ${distributorId ? 'update' : 'add'} distributor`);
            }
        })
        .catch(error => {
            console.error('Error saving distributor:', error);
            showAlert('error', `Failed to ${distributorId ? 'update' : 'add'} distributor`);
        });
}

// Load orders data
function loadOrders() {
    // Load customer orders
    fetch('/api/orders/customer')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateCustomerOrdersTable(data.orders);
            } else {
                showAlert('error', 'Failed to load customer orders');
            }
        })
        .catch(error => {
            console.error('Error loading customer orders:', error);
            showAlert('error', 'Failed to load customer orders');
        });
    
    // Load distributor orders
    fetch('/api/orders/distributor')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateDistributorOrdersTable(data.orders);
            } else {
                showAlert('error', 'Failed to load distributor orders');
            }
        })
        .catch(error => {
            console.error('Error loading distributor orders:', error);
            showAlert('error', 'Failed to load distributor orders');
        });
}

// Load configuration
function loadConfig() {
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateConfigForm(data.config);
            } else {
                showAlert('error', 'Failed to load configuration');
            }
        })
        .catch(error => {
            console.error('Error loading configuration:', error);
            showAlert('error', 'Failed to load configuration');
        });
}

// Update configuration form
function updateConfigForm(config) {
    document.getElementById('lowStockThreshold').value = config.low_stock_threshold;
    document.getElementById('taxRate').value = config.tax_rate;
    document.getElementById('defaultMargin').value = config.default_margin;
    document.getElementById('apiKey').value = config.api_key;
    document.getElementById('apiEndpoint').value = config.api_endpoint;
    document.getElementById('emailNotifications').checked = config.email_notifications;
    document.getElementById('lowStockAlerts').checked = config.low_stock_alerts;
    document.getElementById('orderNotifications').checked = config.order_notifications;
}

// Handle save configuration
function handleSaveConfig(e) {
    e.preventDefault();
    
    const configData = {
        low_stock_threshold: parseInt(document.getElementById('lowStockThreshold').value),
        tax_rate: parseFloat(document.getElementById('taxRate').value),
        default_margin: parseFloat(document.getElementById('defaultMargin').value),
        api_key: document.getElementById('apiKey').value,
        api_endpoint: document.getElementById('apiEndpoint').value,
        email_notifications: document.getElementById('emailNotifications').checked,
        low_stock_alerts: document.getElementById('lowStockAlerts').checked,
        order_notifications: document.getElementById('orderNotifications').checked
    };
    
    fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(configData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', 'Configuration saved successfully');
        } else {
            showAlert('error', data.message || 'Failed to save configuration');
        }
    })
    .catch(error => {
        console.error('Error saving configuration:', error);
        showAlert('error', 'Failed to save configuration');
    });
}

// Toggle API key visibility
function toggleApiKeyVisibility() {
    const apiKeyInput = document.getElementById('apiKey');
    const toggleButton = document.getElementById('toggleApiKey');
    
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        toggleButton.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        apiKeyInput.type = 'password';
        toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Show alert
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.main-content').insertAdjacentElement('afterbegin', alertDiv);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Edit store
function editStore(storeId) {
    fetch(`/api/stores/${storeId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const store = data.store;
                document.getElementById('storeId').value = store.id;
                document.getElementById('storeName').value = store.store_name;
                document.getElementById('countryCode').value = store.country_code;
                document.getElementById('currencyCode').value = store.currency_code;
                
                document.getElementById('addStoreModalLabel').textContent = 'Edit Store';
                bootstrap.Modal.getInstance(document.getElementById('addStoreModal')).show();
            } else {
                showAlert('danger', data.message || 'Failed to load store details');
            }
        })
        .catch(error => {
            console.error('Error loading store:', error);
            showAlert('danger', 'Failed to load store details');
        });
}

// Delete store
function deleteStore(storeId) {
    if (confirm('Are you sure you want to delete this store?')) {
        fetch(`/api/stores/${storeId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showAlert('success', 'Store deleted successfully');
                loadStores();
            } else {
                showAlert('danger', data.message || 'Failed to delete store');
            }
        })
        .catch(error => {
            console.error('Error deleting store:', error);
            showAlert('danger', 'Failed to delete store');
        });
    }
}

// Activate store
function activateStore(storeId) {
    fetch(`/api/stores/${storeId}/activate`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', 'Store activated successfully');
            loadStores();
        } else {
            showAlert('danger', data.message || 'Failed to activate store');
        }
    })
    .catch(error => {
        console.error('Error activating store:', error);
        showAlert('danger', 'Failed to activate store');
    });
}

// Store selection function
function selectStore(countryCode) {
    // Show loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <div class="loading-text">Switching store...</div>
    `;
    document.body.appendChild(loadingOverlay);
    
    // Disable all store cards
    document.querySelectorAll('.store-card').forEach(card => {
        card.style.pointerEvents = 'none';
        card.style.opacity = '0.7';
    });
    
    fetch('/api/stores/' + countryCode + '/activate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Immediately refresh the page
            window.location.reload();
        } else {
            showAlert('danger', data.message || 'Failed to switch store');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Failed to switch store');
    })
    .finally(() => {
        // Remove loading overlay and re-enable store cards
        document.body.removeChild(loadingOverlay);
        document.querySelectorAll('.store-card').forEach(card => {
            card.style.pointerEvents = 'auto';
            card.style.opacity = '1';
        });
    });
}

// Reset database function
function resetDatabase() {
    if (!confirm('Are you sure you want to reset the database? This will delete all data and restore the initial configuration.')) {
        return;
    }

    const btn = document.getElementById('resetDatabaseBtn');
    const originalText = btn.innerHTML;
    
    // Disable button and show loading state
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Resetting...';
    
    fetch('/api/reset_database', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Show success message
            btn.innerHTML = '<i class="fas fa-check me-2"></i>Reset Successful';
            btn.classList.remove('btn-danger');
            btn.classList.add('btn-success');
            
            // Reload page after 1.5 seconds
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            throw new Error(data.message || 'Failed to reset database');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Show error message
        btn.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>Reset Failed';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-warning');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            btn.classList.remove('btn-warning');
            btn.classList.add('btn-danger');
        }, 2000);
        
        // Show error alert
        const errorMessage = document.createElement('div');
        errorMessage.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x';
        errorMessage.style.zIndex = '9999';
        errorMessage.innerHTML = `
            <strong>Error!</strong> ${error.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(errorMessage);
        
        // Remove error message after 3 seconds
        setTimeout(() => {
            errorMessage.remove();
        }, 3000);
    });
}


function loadMasterTable() {
    const tableSelect = document.getElementById('masterTableSelect');
    const selectedTable = tableSelect.value;
    const contentDiv = document.getElementById('masterTableContent');

    if (!selectedTable) {
        contentDiv.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-database fa-3x mb-3"></i>
                <p>Select a master table to view its records</p>
            </div>
        `;
        return;
    }

    // Show loading state
    contentDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;

    // Fetch data from the server
    fetch(`/api/${selectedTable}`)
        .then(response => response.json())
        .then(data => {
            console.log('API Response:', data); // Debugging line
            if (data.status === 'success') {
                const tableHtml = generateTableHtml(selectedTable, data[selectedTable]);
                contentDiv.innerHTML = tableHtml;
            } else {
                contentDiv.innerHTML = `
                    <div class="alert alert-danger">
                        Error loading ${selectedTable}: ${data.message}
                    </div>
                `;
            }
        })
        .catch(error => {
            contentDiv.innerHTML = `
                <div class="alert alert-danger">
                    Error loading ${selectedTable}: ${error.message}
                </div>
            `;
        });
}



function generateTableHtml(tableName, records) {
    console.log(records); // Debugging line
    let headers = [];
    let rows = [];

    switch (tableName) {
        case 'distributors':
            headers = ['Name', 'Contact Person', 'Email', 'Phone', 'Address', 'Actions'];
            rows = records.map(record => [
                record.name,
                record.contact_person || '-',
                record.email,
                record.phone || '-',
                record.address || '-',
                generateActionButtons(record.id)
            ]);
            break;
        case 'customers':
            headers = ['Name', 'Email', 'Phone', 'Address', 'Actions'];
            rows = records.map(record => [
                record.name,
                record.email,
                record.phone || '-',
                record.address || '-',
                generateActionButtons(record.id)
            ]);
            break;
        case 'categories':
            headers = ['Name', 'Description', 'Actions'];
            rows = records.map(record => [
                record.name,
                record.description || '-',
                generateActionButtons(record.id)
            ]);
            break;
        case 'units':
            headers = ['Name', 'Symbol', 'Actions'];
            rows = records.map(record => [
                record.name,
                record.symbol || '-',
                generateActionButtons(record.id)
            ]);
            break;
        case 'products': // Add case for products
            headers = ['SKU', 'Name', 'Category', 'Base Price', 'Cost Price', 'Stock Level', 'Actions'];
            rows = records.map(record => [
                record.sku,
                record.name,
                record.category || '-',
                record.price ? `$${record.price.toFixed(2)}` : 'N/A', 
                formatCurrency(record.cost_price),
                record.quantity || '0',
                generateActionButtons(record.id)
            ]);
            break;
    }

    return `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        ${headers.map(header => `<th>${header}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            ${row.map(cell => `<td>${cell}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function generateActionButtons(id) {
    return `
        <div class="btn-group">
            <button class="btn btn-sm btn-outline-primary" onclick="editRecord(${id})">
                <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteRecord(${id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
}




function showAddMasterForm() {
    const selectedTable = document.getElementById('masterTableSelect').value;

    if (!selectedTable) {
        alert('Please select a master table first');
        return;
    }

    let modal = document.getElementById('addMasterModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'addMasterModal';
        modal.className = 'modal fade';
        document.body.appendChild(modal);
    }

    let formFields = '';
    switch (selectedTable) {
        case 'distributors':
            formFields = `
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" required>
                </div>
                <div class="mb-3">
                    <label for="contactPerson" class="form-label">Contact Person</label>
                    <input type="text" class="form-control" id="contact_person" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" required>
                </div>
                <div class="mb-3">
                    <label for="phone" class="form-label">Phone</label>
                    <input type="text" class="form-control" id="phone" required>
                </div>
                <div class="mb-3">
                    <label for="address" class="form-label">Address</label>
                    <textarea class="form-control" id="address" rows="3" required></textarea>
                </div>
            `;
            break;
        case 'customers':
            formFields = `
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" required>
                </div>
                <div class="mb-3">
                    <label for="phone" class="form-label">Phone</label>
                    <input type="text" class="form-control" id="phone" required>
                </div>
                <div class="mb-3">
                    <label for="address" class="form-label">Address</label>
                    <textarea class="form-control" id="address" rows="3" required></textarea>
                </div>
            `;
            break;
        case 'categories':
            formFields = `
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">Description</label>
                    <textarea class="form-control" id="description" rows="3"></textarea>
                </div>
            `;
            break;
        case 'units':
            formFields = `
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" required>
                </div>
                <div class="mb-3">
                    <label for="symbol" class="form-label">Symbol</label>
                    <input type="text" class="form-control" id="symbol" required>
                </div>
            `;
            break;
        case 'products': // Add case for products
            formFields = `
                <div class="mb-3">
                    <label for="sku" class="form-label">SKU</label>
                    <input type="text" class="form-control" id="sku" required>
                </div>
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" required>
                </div>
                <div class="mb-3">
                    <label for="category" class="form-label">Category</label>
                    <input type="text" class="form-control" id="category" required>
                </div>
                <div class="mb-3">
                    <label for="price" class="form-label">Base Price</label>
                    <input type="number" class="form-control" id="price" required>
                </div>
                <div class="mb-3">
                    <label for="cost_price" class="form-label">Cost Price</label>
                    <input type="number" class="form-control" id="cost_price" required>
                </div>
                <div class="mb-3">
                    <label for="quantity" class="form-label">Stock Level</label>
                    <input type="number" class="form-control" id="quantity" required>
                </div>
            `;
            break;
        // Add other cases as needed...
    

    }

    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New ${selectedTable.charAt(0).toUpperCase() + selectedTable.slice(1)}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="addMasterForm">
                        ${formFields}
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="submitAdd('${selectedTable}')">Save</button>
                </div>
            </div>
        </div>
    `;

    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}


function submitAdd(selectedTable) {
    const formData = {};
    document.querySelectorAll('#addMasterForm input, #addMasterForm textarea').forEach(input => {
        formData[input.id] = input.value;
    });

    const url = `/api/${selectedTable}/add`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(`${selectedTable.charAt(0).toUpperCase() + selectedTable.slice(1)} added successfully!`);
                loadMasterTable(); // Reload the table to reflect changes
                bootstrap.Modal.getInstance(document.getElementById('addMasterModal')).hide(); // Close the modal
            } else {
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error(`Error adding record:`, error);
            alert('An unexpected error occurred.');
        });
}

function submitUpdate(selectedTable, id) {
    const formData = {};
    document.querySelectorAll('#updateMasterForm input, #updateMasterForm textarea').forEach(input => {
        formData[input.id] = input.value;
    });

    const url = `/api/${selectedTable}/${id}`;

    fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(`${selectedTable.charAt(0).toUpperCase() + selectedTable.slice(1)} updated successfully!`);
                loadMasterTable(); // Reload the table to reflect changes
                bootstrap.Modal.getInstance(document.getElementById('updateMasterModal')).hide(); // Close the modal
            } else {
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error(`Error updating record:`, error);
            alert('An unexpected error occurred.');
        });
}


function getMasterTableDataById(tableName, id) {
    if (!tableName || !id) {
        console.error('Table name or ID is missing');
        return;
    }

    // Fetch the record details by ID
    fetch(`/api/${tableName}/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log(`Data for ${tableName} with ID ${id}:`, data.record);
                // You can use the fetched data here, e.g., populate a form or display it in the UI
                populateFormWithData(tableName, data.record);
            } else {
                alert(`Error fetching data: ${data.message}`);
            }
        })
        .catch(error => {
            console.error(`Error fetching data for ${tableName} with ID ${id}:`, error);
            // alert('An unexpected error occurred while fetching the data.');
        });
}

function populateFormWithData(tableName, record) {
    // Clear the form first
    document.querySelectorAll('#addMasterForm input, #addMasterForm textarea').forEach(input => {
        input.value = '';
    });

    // Populate the form fields based on the table
    switch (tableName) {
        case 'distributors':
            document.getElementById('name').value = record.name || '';

            document.getElementById('contact_person').value = record.contact_person || '';
            document.getElementById('email').value = record.email || '';
            document.getElementById('phone').value = record.phone || '';
            document.getElementById('address').value = record.address || '';
            break;
        case 'customers':
            document.getElementById('name').value = record.name || '';
            document.getElementById('email').value = record.email || '';
            document.getElementById('phone').value = record.phone || '';
            document.getElementById('address').value = record.address || '';
            break;
        case 'categories':
            document.getElementById('name').value = record.name || '';
            document.getElementById('description').value = record.description || '';
            break;
        case 'units':
            document.getElementById('name').value = record.name || '';
            document.getElementById('symbol').value = record.symbol || '';
            break;
        case 'products':
            document.getElementById('sku').value = record.sku || '';
            document.getElementById('name').value = record.name || '';
            document.getElementById('category').value = record.category || '';
            document.getElementById('price').value = record.price || '';
            document.getElementById('cost_price').value = record.cost_price || '';
            document.getElementById('quantity').value = record.quantity || '';
            break;
        default:
            console.error('Unknown table name:', tableName);
    }
}

function editRecord(id) {
    const selectedTable = document.getElementById('masterTableSelect').value;

    if (!selectedTable) {
        alert('Please select a master table first');
        return;
    }

    // Fetch the record details and populate the form
    getMasterTableDataById(selectedTable, id);

    // Show the modal for editing
    showUpdateMasterForm(selectedTable, id);
}

function showUpdateMasterForm(tableName, id) {
    if (!tableName || !id) {
        alert('Table name or ID is missing');
        return;
    }

    // Fetch the record details by ID
    fetch(`/api/${tableName}/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const record = data.record;

                // Create or get the modal element
                let modal = document.getElementById('updateMasterModal');
                if (!modal) {
                    modal = document.createElement('div');
                    modal.id = 'updateMasterModal';
                    modal.className = 'modal fade';
                    document.body.appendChild(modal);
                }

                // Generate form fields based on the table
                let formFields = '';
                switch (tableName) {
                    case 'distributors':
                        formFields = `
                            <div class="mb-3">
                                <label for="name" class="form-label">Name</label>
                                <input type="text" class="form-control" id="name" value="${record.name || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label for="contactPerson" class="form-label">Contact Person</label>
                                <input type="text" class="form-control" id="contact_person" value="${record.contact_person || ''}">
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" value="${record.email || ''}">
                            </div>
                            <div class="mb-3">
                                <label for="phone" class="form-label">Phone</label>
                                <input type="text" class="form-control" id="phone" value="${record.phone || ''}">
                            </div>
                            <div class="mb-3">
                                <label for="address" class="form-label">Address</label>
                                <textarea class="form-control" id="address" rows="3">${record.address || ''}</textarea>
                            </div>
                        `;
                        break;
                    case 'customers':
                        formFields = `
                            <div class="mb-3">
                                <label for="name" class="form-label">Name</label>
                                <input type="text" class="form-control" id="name" value="${record.name || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" value="${record.email || ''}">
                            </div>
                            <div class="mb-3">
                                <label for="phone" class="form-label">Phone</label>
                                <input type="text" class="form-control" id="phone" value="${record.phone || ''}">
                            </div>
                            <div class="mb-3">
                                <label for="address" class="form-label">Address</label>
                                <textarea class="form-control" id="address" rows="3">${record.address || ''}</textarea>
                            </div>
                        `;
                        break;
                    case 'categories':
                        formFields = `
                            <div class="mb-3">
                                <label for="name" class="form-label">Name</label>
                                <input type="text" class="form-control" id="name" value="${record.name || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label for="description" class="form-label">Description</label>
                                <textarea class="form-control" id="description" rows="3">${record.description || ''}</textarea>
                            </div>
                        `;
                        break;
                    case 'units':
                        formFields = `
                            <div class="mb-3">
                                <label for="name" class="form-label">Name</label>
                                <input type="text" class="form-control" id="name" value="${record.name || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label for="symbol" class="form-label">Symbol</label>
                                <input type="text" class="form-control" id="symbol" value="${record.symbol || ''}">
                            </div>
                        `;
                        break;
                    case 'products':
                        formFields = `
                            <div class="mb-3">
                                <label for="sku" class="form-label">SKU</label>
                                <input type="text" class="form-control" id="sku" value="${record.sku || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label for="name" class="form-label">Name</label>
                                <input type="text" class="form-control" id="name" value="${record.name || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label for="category" class="form-label">Category</label>
                                <input type="text" class="form-control" id="category" value="${record.category || ''}">
                            </div>
                            <div class="mb-3">
                                <label for="price" class="form-label">Base Price</label>
                                <input type="number" class="form-control" id="price" value="${record.price || ''}">
                            </div>
                            <div class="mb-3">
                                <label for="cost_price" class="form-label">Cost Price</label>
                                <input type="number" class="form-control" id="cost_price" value="${record.cost_price || ''}">
                            </div>
                            <div class="mb-3">
                                <label for="quantity" class="form-label">Stock Level</label>
                                <input type="number" class="form-control" id="quantity" value="${record.quantity || ''}">
                            </div>
                        `;
                        break;
                    default:
                        alert('Unknown table name');
                        return;
                }

                // Populate the modal with the form
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Update ${tableName.charAt(0).toUpperCase() + tableName.slice(1)}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <form id="updateMasterForm">
                                    ${formFields}
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="button" class="btn btn-primary" onclick="submitUpdate('${tableName}', ${id})">Save Changes</button>
                            </div>
                        </div>
                    </div>
                `;

                // Show the modal
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();
            } else {
                alert(`Error fetching data: ${data.message}`);
            }
        })
        .catch(error => {
            console.error(`Error fetching data for ${tableName} with ID ${id}:`, error);
            // alert('An unexpected error occurred while fetching the data.');
        });
}

function deleteRecord(id) {
    const selectedTable = document.getElementById('masterTableSelect').value;

    if (!selectedTable) {
        alert('Please select a master table first');
        return;
    }

    if (confirm('Are you sure you want to delete this record?')) {
        // Send a DELETE request to the server
        fetch(`/api/${selectedTable}/${id}`, {
            method: 'DELETE',
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(`${selectedTable.charAt(0).toUpperCase() + selectedTable.slice(1)} deleted successfully!`);
                    loadMasterTable(); // Reload the table to reflect changes
                } else {
                    alert(`Error: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Error deleting record:', error);
                // alert('An unexpected error occurred while deleting the record.');
            });
    }
}