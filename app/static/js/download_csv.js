// Function to convert JSON objects to CSV format
function jsonToCsv(jsonData, columnOrder = null) {
    if (!Array.isArray(jsonData) || jsonData.length === 0) {
        return '';
    }
    
    // Use provided column order if available, otherwise fallback to Object.keys
    const headers = columnOrder || Object.keys(jsonData[0]);
    
    // Create CSV header row
    const csvHeaders = headers.map(header => `"${header}"`).join(',');
    
    // Create CSV data rows
    const csvRows = jsonData.map(row => {
        return headers.map(header => {
            const value = row[header];
            // Handle null/undefined values and escape quotes
            if (value === null || value === undefined) {
                return '""';
            }
            // Convert to string and escape quotes
            const stringValue = String(value).replace(/"/g, '""');
            return `"${stringValue}"`;
        }).join(',');
    });
    
    // Combine headers and rows
    return [csvHeaders, ...csvRows].join('\n');
}

document.addEventListener('DOMContentLoaded', () => {
    const downloadButton = document.getElementById('download-csv');
    downloadButton.addEventListener('click', () => {
        const key = sessionStorage.getItem('merge_result_key');
        console.log('Downloading CSV for key:', key);
        
        // Extract column order from the displayed table
        const displayedTable = document.getElementById('data-viewer-result-popup');
        let columnOrder = null;
        
        if (displayedTable) {
            const headerRow = displayedTable.querySelector('thead tr');
            if (headerRow) {
                columnOrder = Array.from(headerRow.querySelectorAll('th')).map(th => th.textContent.trim());
                console.log('Using column order from displayed table:', columnOrder);
            }
        }
        
        fetch(`/api/data/get/merge_result/${key}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.blob();
            })
            .then(async blob => {
                const data = await blob.text();
                const jsonData = JSON.parse(data);
                const csvData = jsonData.merged_data;
                console.log('CSV Data:', csvData); // For debugging
                
                // Validate that csvData exists and is not empty
                if (!csvData || (Array.isArray(csvData) && csvData.length === 0)) {
                    throw new Error('No CSV data available to download');
                }
                
                // Convert JSON objects to CSV format using the same column order as displayed
                const csvString = jsonToCsv(csvData, columnOrder);
                
                // Add UTF-8 BOM for better Excel compatibility
                const csvBlob = new Blob(['\uFEFF' + csvString], { type: 'text/csv;charset=utf-8;' });
                const url = window.URL.createObjectURL(csvBlob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'merged_results.csv';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error downloading CSV:', error);
            });
    });
});