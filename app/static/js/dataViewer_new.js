// populate table description and save it for later use
function populateTableDescription(tableDescriptions) {
    const tableDescTbody = document.getElementById('table-description-div').getElementsByTagName('tbody')[0];

    tableDescriptions.forEach(desc => {
        const row = document.createElement('tr');

        const tableNameCell = document.createElement('td');
        tableNameCell.textContent = desc.table_name;
        row.appendChild(tableNameCell);

        const tableTypeCell = document.createElement('td');
        tableTypeCell.textContent = desc.table_type;
        row.appendChild(tableTypeCell);

        const keyIdentifiersCell = document.createElement('td');
        keyIdentifiersCell.textContent = desc.key_columns.key_list.join(', ');
        row.appendChild(keyIdentifiersCell);

        const descriptionCell = document.createElement('td');
        descriptionCell.textContent = desc.description;
        row.appendChild(descriptionCell);

        const checkButtonCell = document.createElement('td');
        const checkTableInput = document.createElement('input');
        checkTableInput.className = 'btn btn-primary btn-sm';
        checkTableInput.type = 'checkbox';
        checkTableInput.value = desc.table_name;
        checkTableInput.checked = false;
        checkButtonCell.appendChild(checkTableInput);
        row.appendChild(checkButtonCell);

        const mainTableCell = document.createElement('td');
        const mainTableInput = document.createElement('input');
        mainTableInput.type = 'radio';
        mainTableInput.name = 'main-table-radio';
        mainTableInput.value = desc.table_name;
        mainTableCell.appendChild(mainTableInput);
        row.appendChild(mainTableCell);

        tableDescTbody.appendChild(row);
    });
}

// populate project selector
function populateProjectSelector(projects) {
    const projectSelect = document.getElementById('project-select');
    projects.forEach(proj => {
        const option = document.createElement('option');
        option.textContent = proj;
        option.value = proj;
        projectSelect.appendChild(option);
    });
}



// fetch initial data: projects, table_descriptions, table_columns
async function fetchInitialData() {
    try {
        const response = await fetch('/api/data/get/data_viewer/init');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        // save data for later use in session storage if needed
        sessionStorage.setItem('dataViewer_initData', JSON.stringify(data));
    } catch (error) {
        console.error('Error fetching initial data:', error);
    }
}

// Populate project selector and table description on page load
async function initializeDataViewer() {
  dataview_init = JSON.parse(sessionStorage.getItem('dataViewer_initData'));
  if (!dataview_init) {
      await fetchInitialData();
      dataview_init = JSON.parse(sessionStorage.getItem('dataViewer_initData'));
  }
  populateProjectSelector(dataview_init.projects);
  document.getElementById('project-select').addEventListener('change', function() {
    if (this.value) {
      // console.log('Selected project:', this.value);
      document.getElementById('table-description-div').getElementsByTagName('tbody')[0].innerHTML = ''; // Clear previous descriptions
      populateTableDescription(dataview_init.tables_description[this.value]);
      document.getElementById('table-description-div').getElementsByTagName('table')[0].style.display = 'block';
    }
  });
}


function gatherSelectedTablesAndColumns() {
    const selectionContainer = document.getElementById('table-description-div');
    const tableRows = selectionContainer.querySelectorAll('input[type="checkbox"]:checked');
    const mainTableSelected = selectionContainer.querySelector('input[type="radio"]:checked');
    if (!mainTableSelected) {
      alert('Please select a main table by clicking the radio button.');
      throw new Error('Main table not selected');
    }
    const selectedProject = document.getElementById('project-select').value;
    const selections = [];
    for (let selectedTable of tableRows) {
        const isMainTable = selectedTable.value === mainTableSelected.value;
        const mergeType = isMainTable ? 'base' : 'left join';
        selections.push({ 
          "tableName": selectedTable.value, 
          "selectedColumns": dataview_init.table_select_options[selectedProject][selectedTable.value] || [], 
          "mergeType": mergeType,
          "keyCols": dataview_init.tables_description[selectedProject].find(t => t.table_name === selectedTable.value).key_columns.key_list
        });
    }
    sessionStorage.setItem('dataViewer_selectedTablesAndColumns', JSON.stringify(selections));
    return selections;
}


function openModalWithContent(title, row) {
  const selectedProject = document.getElementById('project-select').value;
  const selectedTable = row.cells[0].textContent;
  const selectedCols = row.cells[1].querySelector('div').textContent.split('\n');
  const keyColG1 = row.cells[2].querySelector('select').value;
  const keyColG2 = row.cells[3].querySelector('select').value;
  const keyColG3 = row.cells[4].querySelector('select').value;
  // const mergeType = row.cells[5].textContent;
  const keyCols = [keyColG1, keyColG2, keyColG3];
  const defaultCols = dataview_init.table_select_options[selectedProject][selectedTable] || [];

  const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.innerHTML = `
      <div class="modal">
        <div class="modal-content">
          <div class="modal-btn-container">
            <button type="button" class="deselect-btn btn-close">Deselect All</button>
            <button type="button" class="select-btn btn-close">Select All</button>
            <button type="button" class="confirm-btn btn-close">Done</button>
          </div>
          <h4 class="modal-title">${title} "${selectedTable}"</h4>
          <div class="modal-container">
            ${defaultCols.map(col => {
              const isChecked = selectedCols.includes(col) ? 'checked' : '';
              const isKeyCol = keyCols.includes(col);
              return `
                <div class="modal-checkbox-row">
                  <label for="col-${col}">${col}</label>
                  <input type="checkbox" class="modal-col-checkbox" id="col-${col}" value="${col}" ${isChecked} ${isKeyCol ? 'disabled' : ''}>
                </div>
              `;
            }).join('\n')}

          </div>
        </div>
      </div>
    `;
    // Event listeners for modal buttons
    modal.querySelector('.deselect-btn').addEventListener('click', () => {
      const checkboxes = modal.querySelectorAll('.modal-col-checkbox');
      checkboxes.forEach(checkbox => {
        if (!keyCols.includes(checkbox.value)) {
          checkbox.checked = false;
        }
      });
    });
    modal.querySelector('.select-btn').addEventListener('click', () => {
      const checkboxes = modal.querySelectorAll('.modal-col-checkbox');
      checkboxes.forEach(checkbox => {
        checkbox.checked = true;
      });
    });
    modal.querySelector('.confirm-btn').addEventListener('click', () => {
      const checkboxes = modal.querySelectorAll('.modal-col-checkbox');
      const selectedColumns = [];
      checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
          selectedColumns.push(checkbox.value);
        }
      });
      // Update the row in the main table
      const scrollableDiv = row.cells[1].querySelector('div');
      scrollableDiv.textContent = selectedColumns.join('\n');
      // Close the modal
      document.body.removeChild(modal);
    });
    document.body.appendChild(modal);

  }


// All Events
document.addEventListener('DOMContentLoaded', () => {
  initializeDataViewer();
  const checkMergeLogicBtn = document.getElementById('check-merge-logic-btn');
  
  checkMergeLogicBtn.addEventListener('click', () => {
    // gather selected tables and columns
    const selections = gatherSelectedTablesAndColumns();
    // console.log('Selections for merge logic check:', selections);
    // display confirm table
    confirmTable.innerHTML = ''; // clear previous content
    confirmTable.parentElement.style.display = 'grid'; // show the confirm table div
    for (let row of selections) {
      // console.log('Adding to confirm table:', row);
      const tr = document.createElement('tr');
      const tableTd = document.createElement('td');
      tableTd.textContent = row.tableName;
      tr.appendChild(tableTd);

      const columnsTd = document.createElement('td');
      const scrollableDiv = document.createElement('div');
      scrollableDiv.style.maxHeight = '50px';
      scrollableDiv.style.overflowY = 'auto';
      scrollableDiv.style.border = '1px solid #ddd';
      scrollableDiv.style.whiteSpace = 'pre-line';
      scrollableDiv.style.paddingLeft = '5px';
      scrollableDiv.textContent = row.selectedColumns.join('\n');
      scrollableDiv.classList.add('selected-columns-box');
      columnsTd.appendChild(scrollableDiv);
      tr.appendChild(columnsTd);

      const keyColG1Td = document.createElement('td');
      const selectG1 = document.createElement('select');
      selectG1.className = 'form-select form-select-sm';
      row.keyCols.forEach((keyCol, index) => {
        const option = document.createElement('option');
        option.value = keyCol;
        option.textContent = keyCol;
        if (index === 0) option.selected = true;
        selectG1.appendChild(option);
      });
      keyColG1Td.appendChild(selectG1);
      tr.appendChild(keyColG1Td);

      const keyColG2Td = document.createElement('td');
      const selectG2 = document.createElement('select');
      selectG2.className = 'form-select form-select-sm';
      row.keyCols.forEach((keyCol, index) => {
        const option = document.createElement('option');
        option.value = keyCol;
        option.textContent = keyCol;
        if (index === 1) option.selected = true;
        selectG2.appendChild(option);
      });
      if (row.keyCols.length < 2) {
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = '-';
        emptyOption.selected = true;
        selectG2.appendChild(emptyOption);
      }
      keyColG2Td.appendChild(selectG2);
      tr.appendChild(keyColG2Td);

      const keyColG3Td = document.createElement('td');
      const selectG3 = document.createElement('select');
      selectG3.className = 'form-select form-select-sm';
      row.keyCols.forEach((keyCol, index) => {
        const option = document.createElement('option');
        option.value = keyCol;
        option.textContent = keyCol;
        if (index === 2) option.selected = true;
        selectG3.appendChild(option);
      });
      if (row.keyCols.length < 3) {
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = '-';
        emptyOption.selected = true;
        selectG3.appendChild(emptyOption);
      }
      keyColG3Td.appendChild(selectG3);
      tr.appendChild(keyColG3Td);

      const actionTd = document.createElement('td');
      actionTd.textContent = row.mergeType;
      tr.appendChild(actionTd);

      confirmTable.appendChild(tr);
    }
    
  });

  // global variables
  const confirmTable = document.getElementById('column-merge-confirm-div').querySelector('tbody');


  document.getElementsByClassName('submit-btn')[0].addEventListener('click', () => {
    // selections = JSON.parse(sessionStorage.getItem('dataViewer_selectedTablesAndColumns'));
    const confirmRows = confirmTable.querySelectorAll('tr');
    const selections = [];
    confirmRows.forEach(row => {
      const tableName = row.cells[0].textContent;
      const selectedColumns = row.cells[1].querySelector('div').textContent.split('\n');
      const keyColG1 = row.cells[2].querySelector('select').value;
      let keyColG2 = null;
      let keyColG3 = null;
      if (row.cells[3].textContent !== '-') {
        keyColG2 = row.cells[3].querySelector('select').value;
      }
      if (row.cells[4].textContent !== '-') {
        keyColG3 = row.cells[4].querySelector('select').value;
      }
      const mergeType = row.cells[row.cells.length -1].textContent;
      selections.push({
        "table_name": tableName,
        "selected_cols": selectedColumns,
        "action": mergeType,
        "m1": keyColG1,
        "m2": keyColG2 ,
        "m3": keyColG3
      });
    });
    console.log('Final selections for data viewing:', selections);
    // send to backend to process and redirect to data viewing page

    fetch('/api/data/action/merge_with_key_cols', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            selected_project: document.getElementById('project-select').value,
            tables: selections
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Redirect to data viewing page
        let key = data.redis_key;
        // console.log(data);
        sessionStorage.setItem('merge_result_key', key);
        let popup = window.open(`/data_viewer_new/result/${key}`, '_blank', 'width=800,height=600');
        fetch(`/data_viewer_new/result/${key}`)
        .then(response => response.text())
        .then(html => {
            popup.document.open();
            popup.document.write(html);
            popup.document.close();
        });
    })
    .catch(error => {
        console.error('Error fetching data for viewing:', error);
    });
  });


  document.addEventListener('dblclick', (event) => {
    const selectedTableRow = event.target.closest('tr');
    console.log('Double clicked on selected row');
    console.log('content:', selectedTableRow);

    openModalWithContent('Selected Columns', selectedTableRow);
    
  });
});
