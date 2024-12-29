function parseDate(dateString) {

    const [datePart, timePart] = dateString.split(' '); 
    if (!datePart || !timePart) {
        return new Date("Invalid Date"); 
    }

    const [day, month, year] = datePart.split('/');
    const [hours, minutes] = timePart.split(':');

    return new Date(`20${year}-${month}-${day}T${hours}:${minutes}:00`);
}
let sortDirection = {}; 

function sortTable(column, type) {
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    sortDirection[column] = !sortDirection[column];

    rows.sort((a, b) => {
        const aValue = a.querySelector(`td[data-column="${column}"]`).innerText.trim();
        const bValue = b.querySelector(`td[data-column="${column}"]`).innerText.trim();
        const aDate = parseDate(aValue);
        const bDate = parseDate(bValue);

        if (type === 'text') {
            return sortDirection[column] 
                ? aValue.localeCompare(bValue) 
                : bValue.localeCompare(aValue);
        } else if (type === 'number') {
            return sortDirection[column]
                ? parseFloat(aValue) - parseFloat(bValue)
                : parseFloat(bValue) - parseFloat(aValue);
        } else if (type === 'date') {
            return sortDirection[column]
                ? parseDate(aValue) - parseDate(bValue)
                : parseDate(bValue) - parseDate(aValue);
        }
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}