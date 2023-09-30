function getDataFromRow(config, row) {
    var data = {};
    config.columnMappings.forEach(function(mapping) {
        var index = config.columnNames.indexOf(mapping.htmlName);
        data[mapping.dbName] = row.cells[index].innerText;
    });
    return data;
}

function initializeTable(config) {
    var originalContent = []; // Array to store original content

    function editRow(button) {
        var row = button.parentNode.parentNode;
        var cells = row.getElementsByTagName('td');

        originalContent = []; // Clear previous content

        for (var i = 0; i < cells.length - 2; i++) {
            cells[i].contentEditable = true;
            originalContent.push(cells[i].innerText); // Store original content
        }

        var editButton = row.querySelector('button:nth-of-type(1)');
        var cancelButton = row.querySelector('button:nth-of-type(2)');
        var saveButton = row.querySelector('button:nth-of-type(3)');
        var deleteButton = row.querySelector('button:nth-of-type(4)');

        editButton.style.display = 'none';
        cancelButton.style.display = 'inline-block';
        saveButton.style.display = 'inline-block';
        deleteButton.style.display = 'none';
    }

    function cancelEdit(button) {
        var row = button.parentNode.parentNode;
        var cells = row.getElementsByTagName('td');

        for (var i = 0; i < cells.length - 2; i++) {
            cells[i].contentEditable = false;
            cells[i].innerText = originalContent[i]; // Restore original content
        }

        var editButton = row.querySelector('button:nth-of-type(1)');
        var cancelButton = row.querySelector('button:nth-of-type(2)');
        var saveButton = row.querySelector('button:nth-of-type(3)');
        var deleteButton = row.querySelector('button:nth-of-type(4)');

        editButton.style.display = 'inline-block';
        cancelButton.style.display = 'none';
        saveButton.style.display = 'none';
        deleteButton.style.display = 'inline-block';
    }

    function saveRow(button) {
        var row = button.parentNode.parentNode;
        var cells = row.getElementsByTagName('td');

        originalContent = []; // Clear original content for this row

        for (var i = 0; i < cells.length - 2; i++) {
            cells[i].contentEditable = false;
            originalContent.push(cells[i].innerText); // Store new original content
        }

        var editButton = row.querySelector('button:nth-of-type(1)');
        var cancelButton = row.querySelector('button:nth-of-type(2)');
        var saveButton = row.querySelector('button:nth-of-type(3)');
        var deleteButton = row.querySelector('button:nth-of-type(4)');

        editButton.style.display = 'inline-block';
        cancelButton.style.display = 'none';
        saveButton.style.display = 'none';
        deleteButton.style.display = 'inline-block';

        // Send a POST request to "/testing"
        var id = row.cells[config.columnNames.indexOf('ID')].innerText; // Assuming ID is in the fourth cell
        var name = row.cells[config.columnNames.indexOf('Name')].innerText;
        var age = row.cells[config.columnNames.indexOf('Age')].innerText;

        fetch(config.endpointEdit, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: id,
                name: name,
                age: age
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
            // Handle the response as needed

            // Check if a redirect is necessary
            if (result.needsRedirect) {
                window.location.href = result.redirectUrl; // Navigate to the new URL
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function deleteRow(button) {
        var row = button.parentNode.parentNode;
        var id = row.cells[config.columnNames.indexOf('ID')].innerText; // Assuming ID is in the fourth cell

        // Prompt for confirmation
        var confirmDelete = confirm("Are you sure you want to delete this row?");

        if (confirmDelete) {
            // Send a POST request to "/delete_row"
            fetch(config.endpointDelete, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: id
                })
            })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                // Handle the response as needed
                // Reload the page or update the UI accordingly
                location.reload();
            })
            .catch(error => console.error('Error:', error));
        }
    }

    // Return functions to be accessible from outside
    return {
        editRow: editRow,
        cancelEdit: cancelEdit,
        saveRow: saveRow,
        deleteRow: deleteRow
    };
}

// Export the functions
module.exports = {
    initializeTable: initializeTable,
    getDataFromRow: getDataFromRow
};