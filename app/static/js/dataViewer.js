// declare global variables
const rowChoicesMap = {};
let rowIdCounter = 1;

// main
document.addEventListener("DOMContentLoaded", function () {
    (async () => {
        await initializeDataViewer();
    })();
});


// functions
function initializeDataViewer() {
    const userLoggedIn = get_cookie("logged_in=");
    if (userLoggedIn !== "true" || !userLoggedIn) {
        console.warn("User not logged in. Skipping fetchWithAuth.");
        return;
    }
    const data = getSessionData('data-viewer-select-options');

    if (data) {
        addTableSelectionRow(data); // initial row
    } else {
        fetchWithAuth("/data_viewer/table_options")
            .then(async response  => {
                const result = await response.json();
                if (!result || !result.data_source) return;
                saveSessionData('data-viewer-select-options', result.data_source);
                addTableSelectionRow(result.data_source); // initial row
            })
            .catch(error => console.error("Error fetching select options:", error));
    }
    
        
}


function addTableSelectionRow(dataOption={}) {
    const tableSelectionContainer = document.getElementById("viewer-selection-container");
    console.log(tableSelectionContainer);
    if (!tableSelectionContainer) {
        console.error("Table selection container not found! Please check html file.");
        return;
    }

    // const rowCount = tableSelectionContainer.childElementCount + 1;
    const rowId = `row-${rowIdCounter++}`;

    const rowDiv = createRowDiv(rowId, "table-selection-row");
    
    const dataSource = createRowSelectElement("Data source", "data_source[]", "table_selection data_source", "table-selection-row-element");
    const tableSource = createRowSelectElement("Table", "table[]", "table_selection table_sgl", "table-selection-row-element");
    // const colFilter = createRowSelectElement("Selected column(s)", "col_lst[]", "table_selection col_filter", "table-selection-row-element", true);
    const colFilter = createRowTextElement("Selected column(s)", rowId, "col_filter selected_cols", "table-selection-row-element");
    const colPop = createModal("Keep column(s)", rowId, "colSelection", "table-selection-row-element");
    console.log(colPop);

    const rmBtn = createRemoveButton(rowId, rowIdCounter, "Remove table");

    const subTopRowDiv = document.createElement("div");
    subTopRowDiv.classList.add("top");
    const subBottomRowDiv = document.createElement("div");
    subBottomRowDiv.classList.add("bottom");

    subTopRowDiv.append(dataSource, tableSource, colPop, rmBtn);
    subBottomRowDiv.append(colFilter);

    rowDiv.append(subTopRowDiv, subBottomRowDiv);
    tableSelectionContainer.appendChild(rowDiv);

    populateParentOptions(dataSource.querySelector("select"), dataOption);
    setupTableChangeHandler(dataSource.querySelector("select"), tableSource.querySelector("select"), dataOption, colFilter.querySelector("input"), rowId);
    // the columns should be only populated if a table is selected
}


function getTableDataOptions() {
    return getSessionData("data-viewer-select-options");
}

function setupTableChangeHandler(dataSourceSelect, tableSourceSelect, dataOption, colFilterSelect, rowId) {
    console.log("dataOption.....", dataOption);
    let selectedDataSource = dataSourceSelect.value;
    console.log(selectedDataSource);
    console.log(Object.keys(dataOption));
    // console.log(Object.keys(dataOption[selectedDataSource]));
    dataSourceSelect.onchange = function() {
        tableSourceSelect.length = 1;
        // tableSourceSelect.options[0] = new Option("Choose an option", "");
        selectedDataSource = this.value;
        console.log(this.value);
        const tableList = Object.keys(dataOption[selectedDataSource]) || [];
        console.log("let's see table list...", tableList);
        tableList.forEach(e => {
            console.log("table name...", e, e.split('/'), e.split('/')[-2]);
            tableSourceSelect.options[tableSourceSelect.options.length] = new Option(e, e);
        })

    }
    
    //get columns once table selected
    tableSourceSelect.onchange = function () {
        const selectedTable = this.value;
        const sourceToUse = dataSourceSelect.value || selectedDataSource;
        fetchColumns(sourceToUse, selectedTable, colFilterSelect, rowId);
    }

}


function fetchColumns(schema, table, colFilterSelect, rowId) {
    // fetch data and save in sessionStorage first
    const key = `table_data_${schema}_${table}`;

    if (sessionStorage.getItem(key) === null) {
        console.log('fetchdata', key, 'session not exists');
        const tableOptions = getSessionData('data-viewer-select-options');
        const columns = tableOptions[schema][table];
        saveSessionData(`table_data_${schema}_${table}`, columns);

    }
    const columnNames = getSessionData(key);
    // const columnNames = Object.keys(data);

    openColumnModal(colFilterSelect.closest(".table-selection-row").id, columnNames, (selectedCols) => {
        console.log("Selected columns for", rowId, selectedCols);
    });

    console.log('column names:', columnNames);
    
}



function openColumnModal(rowId, columns, onConfirm) {
    const modal = document.getElementById(`colSelectionModal_${rowId}`);
    const container = document.getElementById(`colSelectionCheckboxContainer_${rowId}`);
    const confirmBtn = document.getElementById(`colSelectionConfirm_${rowId}`);
    const closeBtn = document.getElementById(`deselectModalBtn_${rowId}`);

    // container.innerHTML = "";

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
        const selected = Array.from(container.querySelectorAll("input:checked")).map(cb => cb.value);
        sessionStorage.setItem(`selectedCols_${rowId}`, JSON.stringify(selected));
        modal.style.display = "none";

        // const selectElem = document.querySelector(`.${rowId}`, ".selected_cols", "input");
        // const choices = selectElem.closest('.choices').choices;
        // const choices = document.querySelector(`#${rowId}`).querySelector('.choices');
        const choices = rowChoicesMap[rowId];
        // Check if Choices has already been initialized
        
        choices.setValue(selected);
        choices.disable();
        // selected.forEach(col => {
        //     choices.setValue([{ value: col, label: col }]);
        //     console.log('set value', col, choices);
        // });

        rowChoicesMap[rowId] = choices;
        console.log("Choices instance", choices);


        if (onConfirm) {onConfirm(selected)};
    };

    closeBtn.onclick = function () {
        Array.from(container.querySelectorAll("input:checked")).forEach(checkbox => {
            checkbox.checked = false;
        });
    };
    // window.onclick = (event) => {
    //     if (event.target == modal) {
    //         modal.style.display = "none";
    //     }
    // };

    modal.style.display = "block";
}


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