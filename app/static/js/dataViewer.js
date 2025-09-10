// declare global variables
const rowChoicesMap = {};
let rowIdCounter = 1;

// main
isLoggedIn().then(loggedIn => {
    if (loggedIn) {
        initializeDataViewer();
    } else {
        console.warn("Not logged in yet.");
    }
});


// functions
async function initializeDataViewer() {
    const resp = await fetch(`/api/data/view/table_options`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    });
    if (!resp.ok) {
        console.error("Failed to fetch table options:", resp.statusText);
        return;
    }
    const result = await resp.json();
    console.log("Table options fetched:", result);
    const data = result.table_select_options;

    if (data) {
        addTableSelectionRow(data); // initial row
    } else {
        return;
    }
}


function addTableSelectionRow(dataOption={}) {
    const tableSelectionContainer = document.getElementById("viewer-selection-container");
    // console.log(tableSelectionContainer);
    if (!tableSelectionContainer) {
        console.error("Table selection container not found! Please check html file.");
        return;
    }

    // const rowCount = tableSelectionContainer.childElementCount + 1;
    const rowId = `row-${rowIdCounter++}`;

    const rowDiv = createRowDiv(rowId, "table-selection-row");

    const dataSchema = createRowSelectElement("Data schema", "data_schema[]", "table_selection data_schema", "table-selection-row-element");
    const dataSource = createRowSelectElement("Data source", "data_source[]", "table_selection data_source", "table-selection-row-element");
    const tableSource = createRowSelectElement("Table", "table[]", "table_selection table_sgl", "table-selection-row-element");
    const colFilter = createRowSelectElement("Selected column(s)", "col_lst[]", "table_selection col_filter", "table-selection-row-element", true);
    const colPop = createModal("Keep column(s)", rowId, "colSelection", "table-selection-row-element");
    const rmBtn = createRemoveButton(rowId, rowIdCounter, "Remove table");

    const subTopRowDiv = document.createElement("div");
    subTopRowDiv.classList.add("top");
    const subBottomRowDiv = document.createElement("div");
    subBottomRowDiv.classList.add("bottom");

    subTopRowDiv.append(dataSchema, dataSource, tableSource, colPop, colFilter, rmBtn);
    // subBottomRowDiv.append(colFilter);

    // rowDiv.append(subTopRowDiv, subBottomRowDiv);
    rowDiv.append(subTopRowDiv);
    tableSelectionContainer.appendChild(rowDiv);
    
    populateOptions(dataSchema.querySelector("select"), dataOption);
    dataSchema.querySelector("select").onchange = function() {
        dataSource.querySelector("select").length = 1;
        tableSource.querySelector("select").length = 1;
        dataSource.querySelector("select").options[0] = new Option("Choose an option", "");
        tableSource.querySelector("select").options[0] = new Option("Choose an option", "");
        populateOptions(dataSource.querySelector("select"), dataOption[dataSchema.querySelector("select").value] || {});
    };
    dataSource.querySelector("select").onchange = function() {
        tableSource.querySelector("select").length = 1;
        tableSource.querySelector("select").options[0] = new Option("Choose an option", "");
        populateOptions(tableSource.querySelector("select"), (dataOption[dataSchema.querySelector("select").value] || {})[dataSource.querySelector("select").value] || {});
    };
    tableSource.querySelector("select").onchange = function() {
        openColumnModal(
            rowId, 
            (dataOption[dataSchema.querySelector("select").value] || {})[dataSource.querySelector("select").value][tableSource.querySelector("select").value] || [], 
            (selectedCols) => {
                console.log("Selected columns for", rowId, selectedCols);

            }
        );
    };
}



// helper functions
function populateOptions(selectElement, dataOption) {
    for (const e in dataOption) {
        selectElement.options[selectElement.options.length] = new Option(e, e);
    }
}


function createModal(title, rowId, modalType, modalCls) {
    const modalDiv = document.createElement('div');
    modalDiv.id = `${modalType}Modal_${rowId}`;
    modalDiv.classList.add(modalCls, "modal");
    modalDiv.style.display = "none";

    const modalContent = document.createElement('div');
    modalContent.classList.add("modal-content");

    const modalClose = document.createElement("button");
    modalClose.innerText = "Deselect All";
    modalClose.id = `deselectModalBtn_${rowId}`;
    modalClose.classList.add(..."deselect btn closebtn".split(" "));

    const modalTitle = document.createElement("h3");
    modalTitle.innerHTML = title;

    const modalContainer = document.createElement("div");
    modalContainer.id = `${modalType}CheckboxContainer_${rowId}`;
    modalContainer.classList.add("modal-container");
    // modalContainer.textContent = "Keep column(s)???";

    const modalBtn = document.createElement("button");
    modalBtn.id = `${modalType}Confirm_${rowId}`;
    modalBtn.classList.add("btn");
    modalBtn.innerText = "Done";

    modalDiv.appendChild(modalContent);
    modalContent.append(modalClose, modalTitle, modalContainer, modalBtn);

    return modalDiv;
}


function openColumnModal(rowId, columns, onConfirm) {
    const modal = document.getElementById(`colSelectionModal_${rowId}`);
    const container = document.getElementById(`colSelectionCheckboxContainer_${rowId}`);
    const confirmBtn = document.getElementById(`colSelectionConfirm_${rowId}`);
    const closeBtn = document.getElementById(`deselectModalBtn_${rowId}`);

    columns.forEach(col => {
        const checkRow = document.createElement('div');
        checkRow.classList.add("modal-checkbox-row");

        const label = document.createElement("label");
        label.textContent = col;

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = col;
        checkbox.checked = true;

        checkRow.appendChild(label);
        checkRow.appendChild(checkbox);
        container.appendChild(checkRow);
    });

    confirmBtn.onclick = function () {
        const colFilterSelect = document.querySelector(`#${rowId} .col_filter`);
        colFilterSelect.length = 0;  // Clear existing options

        const selected = {};
        Array.from(container.querySelectorAll("input:checked")).forEach(cb => {
            selected[cb.value] = cb.value;
        });
        // sessionStorage.setItem(`selectedCols_${rowId}`, JSON.stringify(selected));
        modal.style.display = "none";
        console.log("Selected columns:", selected);
        populateOptions(colFilterSelect, selected);

        if (onConfirm) {onConfirm(selected)};
    };

    closeBtn.onclick = function () {
        Array.from(container.querySelectorAll("input:checked")).forEach(checkbox => {
            checkbox.checked = false;
        });
    };

    modal.style.display = "block";
}

document.addEventListener('dblclick', function(event) {
    const row = event.target.closest('.table-selection-row');
    if (row) {
        const rowId = row.id;
        const modal = document.getElementById(`colSelectionModal_${rowId}`);
        const selectedTable = row.querySelector('[name="table[]"]').value;
        if (modal && selectedTable != "Choose an option" && selectedTable != "") {
            modal.style.display = "block";
        }
    }
});


function displayMergedTable() {
    const tables = document.querySelectorAll(".table-selection-row");
    let tableSelections = Object();
    tables.forEach(row => {
        let tableNameKey = String();
        const selectedDataSource = row.querySelector('[name="data_source[]"]').value;
        console.log(selectedDataSource);
        const selectedTable = row.querySelector('[name="table[]"]').value;
        console.log(selectedTable);
        tableNameKey = `table_data_${selectedDataSource}-${selectedTable}`;
        console.log(tableNameKey);
        const rowId = row.id;
        console.log(rowId);

        data = getSessionData(tableNameKey);
        const selectedCols = getSessionData(`selectedCols_${rowId}`);
        tableSelections[tableNameKey] = selectedCols;
    })
    console.log(tableSelections);
    fetch('/data_viewer/merge', {
        method: "POST",
        headers: {
            'Content-Type': "application/json",
        },
        body: JSON.stringify(tableSelections)
    })
    .then(resp => {
        console.log('response...', resp);
        return resp.json();
    })
    // .then(respJson => {
    //     console.log("Merge result key:", respJson.key);
    //     saveSessionData("data_key", respJson.key);
    //     return fetch(`/data_viewer/download/${respJson.key}`);
    // })
    // .then(resp => resp.json())
    .then(result => {
        // console.log("Merged Data:", result.data);
        // render to table here
        saveSessionData("merged_key", result.key);
        loadDashFrame(result.key);
    })
    .catch(error => console.error("Error during merge/download:", error));

}


function loadDashFrame(key) {
    const dashUrl = `/dash_viewer/${key}`;
    document.getElementById('dash-frame').src = dashUrl;
}