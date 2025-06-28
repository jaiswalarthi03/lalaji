// Currency conversion functionality
document.addEventListener('DOMContentLoaded', function() {
    // Load currency rates when modal is shown
    document.getElementById('currencyModal').addEventListener('shown.bs.modal', loadCurrencyRates);
});

function loadCurrencyRates() {
    fetch('/currency/rates')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('currencyRatesTable');
            table.innerHTML = '';
            
            data.rates.forEach(rate => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${rate.from_currency}</td>
                    <td>${rate.to_currency}</td>
                    <td><input type="number" class="form-control" value="${rate.rate}" step="0.0001"></td>
                    <td>${new Date(rate.last_updated).toLocaleString()}</td>
                `;
                table.appendChild(row);
            });
        });
}

function convertCurrency() {
    const amount = parseFloat(document.getElementById('convertAmount').value);
    const fromCurrency = document.getElementById('convertFrom').value;
    const toCurrency = document.getElementById('convertTo').value;
    
    fetch(`/currency/convert?amount=${amount}&from=${fromCurrency}&to=${toCurrency}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('conversionResult').innerHTML = `
                <div class="alert alert-success">
                    ${amount} ${fromCurrency} = ${data.result.toFixed(2)} ${toCurrency}
                </div>
            `;
        });
}

function saveCurrencyRates() {
    const rates = [];
    const rows = document.getElementById('currencyRatesTable').rows;
    
    for (let row of rows) {
        const cells = row.cells;
        rates.push({
            from_currency: cells[0].textContent,
            to_currency: cells[1].textContent,
            rate: parseFloat(cells[2].querySelector('input').value)
        });
    }
    
    fetch('/currency/rates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rates: rates })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Currency rates updated successfully!');
            loadCurrencyRates();
        } else {
            alert('Error updating currency rates');
        }
    });
} 