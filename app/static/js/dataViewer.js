/**
 * Data Viewer Component
 * Handles project selection and table viewing functionality
 */
class DataViewer {
  constructor() {
    // Private properties
    this.rowIdCounter = 1;
    this.tableDataOptions = {};
    this.selectedProject = null;
    
    // DOM element references
    this.projectContainer = document.getElementById("viewer-project-container");
    this.tableSelectionContainer = document.getElementById("viewer-selection-container");
    
    // Bind methods to maintain 'this' context
    this.handleProjectChange = this.handleProjectChange.bind(this);
    this.handleDataSourceChange = this.handleDataSourceChange.bind(this);
    this.handleTableSourceChange = this.handleTableSourceChange.bind(this);
    this.handleModalConfirm = this.handleModalConfirm.bind(this);
    
    // Initialize
    this.init();
  }
  
  async init() {
    try {
      const loggedIn = await isLoggedIn();
      if (loggedIn) {
        await this.getTableDataOptions();
        await this.initializeDataViewer();
      } else {
        console.warn("Not logged in yet.");
      }
    } catch (error) {
      console.error("Initialization error:", error);
    }
  }
  
  async getTableDataOptions() {
    try {
      const resp = await fetch(`/api/data/get/table_options`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      });
      
      if (!resp.ok) {
        throw new Error(`Failed to fetch table options: ${resp.statusText}`);
      }
      
      const result = await resp.json();
      return result.table_select_options;
    } catch (error) {
      console.error("Error fetching table options:", error);
      return null;
    }
  }
  
  async initializeDataViewer() {
    this.tableDataOptions = await this.getTableDataOptions();
    
    if (!this.tableDataOptions) {
      console.error("Failed to load table data options");
      return;
    }
    
    this.addProjectSelection();
    this.addTableSelectionRow();
  }
  
  addProjectSelection() {
    if (!this.projectContainer) {
      console.error("Project container not found! Please check html file.");
      return;
    }
    
    const projectDiv = this.createRowDiv("project-row", "project-row");
    const projectSelect = createRowSelectElement(
      "Select Your Project", 
      "project[]", 
      "project_select", 
      "project-row-element"
    );
    
    this.populateOptions(projectSelect.querySelector("select"), this.tableDataOptions);
    
    // Add change event listener
    const selectElement = projectSelect.querySelector("select");
    selectElement.addEventListener("change", this.handleProjectChange);
    
    projectDiv.appendChild(projectSelect);
    this.projectContainer.appendChild(projectDiv);
  }
  
  handleProjectChange(event) {
    const selectedProject = event.target.value;
    // console.log("Selected project:", selectedProject);
    
    // Store selected project
    this.selectedProject = selectedProject;
    
    // Clear all table selection rows
    this.tableSelectionContainer.innerHTML = "";

    // clear output view
    document.getElementById('dash-frame').src = "";
    
    // Add a new empty row
    this.addTableSelectionRow();
  }
  
  addTableSelectionRow() {
    if (!this.tableSelectionContainer) {
      console.error("Table selection container not found!");
      return;
    }
    
    const rowId = `row-${this.rowIdCounter++}`;
    const rowDiv = this.createRowDiv(rowId, "table-selection-row");
    
    // Create row elements
    const dataSource = createRowSelectElement(
      "Data source", 
      "data_source[]", 
      "table_selection data_source", 
      "table-selection-row-element"
    );
    
    const tableSource = createRowSelectElement(
      "Table", 
      "table[]", 
      "table_selection table_sgl", 
      "table-selection-row-element"
    );
    
    const colFilter = createRowSelectElement(
      "Selected column(s)", 
      "col_lst[]", 
      "table_selection col_filter", 
      "table-selection-row-element", 
      true, 
      `cols_${rowId}`
    );
    
    const colPop = this.createModal("Keep column(s)", rowId, "colSelection", "table-selection-row-element");
    const rmBtn = this.createRemoveButton(rowId);
    
    // Structure the row
    const subTopRowDiv = document.createElement("div");
    subTopRowDiv.classList.add("top");
    
    subTopRowDiv.append(dataSource, tableSource, colPop, colFilter, rmBtn);
    rowDiv.appendChild(subTopRowDiv);
    
    this.tableSelectionContainer.appendChild(rowDiv);
    
    // Set up event handlers for this row
    const dataSourceSelect = dataSource.querySelector("select");
    const tableSourceSelect = tableSource.querySelector("select");
    
    // Initial population of data source options if project is selected
    if (this.selectedProject) {
      const dataOptions = this.tableDataOptions[this.selectedProject] || {};
      this.populateOptions(dataSourceSelect, dataOptions);
    }
    
    // Set event handlers
    dataSourceSelect.addEventListener("change", (e) => this.handleDataSourceChange(e, rowId, tableSourceSelect));
    tableSourceSelect.addEventListener("change", (e) => this.handleTableSourceChange(e, rowId));
  }
  
  handleDataSourceChange(event, rowId, tableSourceSelect) {
    const selectedDataSource = event.target.value;
    
    // Reset and repopulate table selection
    tableSourceSelect.length = 1;
    tableSourceSelect.options[0] = new Option("Choose an option", "");
    
    if (this.selectedProject && selectedDataSource) {
      const tableOptions = (this.tableDataOptions[this.selectedProject] || {})[selectedDataSource] || {};
      this.populateOptions(tableSourceSelect, tableOptions);
    }
  }
  
  handleTableSourceChange(event, rowId) {
    const tableSelect = event.target;
    const row = document.getElementById(rowId);
    const dataSourceSelect = row.querySelector('[name="data_source[]"]');
    
    if (!tableSelect.value || tableSelect.value === "Choose an option") {
      return;
    }
    
    const selectedDataSource = dataSourceSelect.value;
    const selectedTable = tableSelect.value;
    
    // Get columns for the selected table
    const columns = 
      (this.tableDataOptions[this.selectedProject] || {})[selectedDataSource][selectedTable] || [];
    
    // Open column selection modal
    this.openColumnModal(rowId, columns, this.handleModalConfirm);
  }
  
  handleModalConfirm(rowId, selectedColumns) {
    const colFilterSelect = document.querySelector(`#${rowId} .col_filter`);
    colFilterSelect.length = 0; // Clear existing options
    this.populateOptions(colFilterSelect, selectedColumns);
  }
  
  createRowDiv(id, className) {
    const div = document.createElement("div");
    div.id = id;
    div.classList.add(className);
    return div;
  }
  
  populateOptions(selectElement, options) {
    if (!options || Object.keys(options).length === 0) {
      return;
    }
    
    Object.entries(options).forEach(([key, value]) => {
      const option = new Option(key, key);
      selectElement.add(option);
    });
  }
  
  createRemoveButton(rowId) {
    const button = document.createElement("button");
    button.type = "button";
    button.classList.add("btn", "remove-btn");
    button.innerHTML = '<i class="fa fa-minus"></i>';
    
    button.addEventListener("click", () => {
      const row = document.getElementById(rowId);
      if (row) {
        row.remove();
      }
    });
    
    return button;
  }
  
  createModal(title, rowId, modalType, modalCls) {
    const modalDiv = document.createElement('div');
    modalDiv.id = `${modalType}Modal_${rowId}`;
    modalDiv.classList.add(modalCls, "modal");
    modalDiv.style.display = "none";

    const modalContent = document.createElement('div');
    modalContent.classList.add("modal-content");

    const modalBtnContainer = document.createElement("div");
    modalBtnContainer.classList.add("modal-btn-container");

    const modalDeselectAllBtn = document.createElement("button");
    modalDeselectAllBtn.innerText = "Deselect All";
    modalDeselectAllBtn.id = `deselectModalBtn_${rowId}`;
    modalDeselectAllBtn.classList.add("deselect", "btn", "closebtn");

    const modalSelectAllBtn = document.createElement("button");
    modalSelectAllBtn.innerText = "Select All";
    modalSelectAllBtn.id = `selectModalBtn_${rowId}`;
    modalSelectAllBtn.classList.add("select", "btn", "closebtn");

    const modalTitle = document.createElement("h3");
    modalTitle.innerHTML = title;

    const modalContainer = document.createElement("div");
    modalContainer.id = `${modalType}CheckboxContainer_${rowId}`;
    modalContainer.classList.add("modal-container");

    const modalBtn = document.createElement("button");
    modalBtn.id = `${modalType}Confirm_${rowId}`;
    modalBtn.classList.add("btn");
    modalBtn.innerText = "Done";

    modalDeselectAllBtn.addEventListener("click", () => {
      Array.from(modalContainer.querySelectorAll("input:checked")).forEach(checkbox => {
        checkbox.checked = checkbox.disabled ? true : false;
      });
    });

    modalSelectAllBtn.addEventListener("click", () => {
      Array.from(modalContainer.querySelectorAll("input:not(:checked)")).forEach(checkbox => {
        checkbox.checked = true;
      });
    });

    modalBtnContainer.append(modalDeselectAllBtn, modalSelectAllBtn);
    modalDiv.appendChild(modalContent);
    modalContent.append(modalBtnContainer, modalTitle, modalContainer, modalBtn);

    return modalDiv;
  }
  
  openColumnModal(rowId, columns, onConfirm) {
    const modal = document.getElementById(`colSelectionModal_${rowId}`);
    const container = document.getElementById(`colSelectionCheckboxContainer_${rowId}`);
    const confirmBtn = document.getElementById(`colSelectionConfirm_${rowId}`);
    
    // Clear existing checkboxes
    container.innerHTML = '';
    
    // Add checkboxes for each column
    columns.forEach(col => {
      const checkRow = document.createElement('div');
      checkRow.classList.add("modal-checkbox-row");

      const label = document.createElement("label");
      label.textContent = col;

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.value = col;
      checkbox.checked = true;

      // Some columns should always be selected
      if (["participant_ID", "visit_date", "visit_type", "row_id"].includes(col)) {
        checkbox.disabled = true;
      }

      checkRow.appendChild(label);
      checkRow.appendChild(checkbox);
      container.appendChild(checkRow);
    });
    
    // Set up confirmation button
    confirmBtn.onclick = () => {
      const selected = {};
      Array.from(container.querySelectorAll("input:checked")).forEach(cb => {
        selected[cb.value] = cb.value;
      });
      
      modal.style.display = "none";
      onConfirm(rowId, selected);
    };
    
    modal.style.display = "block";
  }
  
  displayMergedTable() {
    const tables = document.querySelectorAll(".table-selection-row");
    const tableSelections = {"schema": this.selectedProject, "tables": {}};
    
    if (!this.selectedProject) {
      alert("Please select a project first.");
      return;
    }
    
    tables.forEach(row => {
      const rowId = row.id;
      const dataSourceSelect = row.querySelector('[name="data_source[]"]');
      const tableSelect = row.querySelector('[name="table[]"]');
      const colListSelect = row.querySelector('[name="col_lst[]"]');
      
      if (!dataSourceSelect?.value || !tableSelect?.value) {
        return;
      }
      
      const selectedCols = Array.from(colListSelect?.options || [])
        .map(option => option.value)
        .filter(Boolean);
        
      if (!selectedCols.length) {
        return;
      }

      tableSelections["tables"][rowId] = {
        "metrics": dataSourceSelect.value,
        "table": tableSelect.value,
        "cols": selectedCols,
      };
    });
    
    if (Object.keys(tableSelections).length === 0) {
      alert("Please select at least one table to view.");
      return;
    }
    
    // check if selected tables are duplicated
    const tableKeys = Object.values(tableSelections["tables"]).map(sel => `${sel.metrics}-${sel.table}`);
    const uniqueTableKeys = new Set(tableKeys);
    if (uniqueTableKeys.size !== tableKeys.length) {
      alert("Please make sure selected tables are not duplicated.");
      return;
    }
    
    // Send merge request
    fetch('/api/data/action/merge', {
      method: "POST",
      headers: {
        'Content-Type': "application/json",
      },
      body: JSON.stringify(tableSelections)
    })
    .then(resp =>  resp.json())
    .then(result => {
      // console.log("Merge result:", result);
      // console.log("Loading Dash frame with key:", result.redis_key);
      this.loadDashFrame(result.redis_key);
    })
    .catch(error => console.error("Error during merge/download:", error));
  }
  
  loadDashFrame(key) {
    const dashUrl = `/dash_viewer/${key}`;
    document.getElementById('dash-frame').src = dashUrl;
    // window.open(dashUrl, '_blank');
  }
}

// Initialize the Data Viewer when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
  const dataViewer = new DataViewer();
  
  const addTableBtn = document.querySelector('.add-btn');
  if (addTableBtn) {
    addTableBtn.addEventListener('click', () => dataViewer.addTableSelectionRow());
  }
  const submitBtn = document.querySelector('.submit-btn');
  if (submitBtn) {
    submitBtn.addEventListener('click', (e) => {
      e.preventDefault();
      dataViewer.displayMergedTable();
    });
  }

  // Set up global double-click handler for opening column modals
  document.addEventListener('dblclick', (event) => {
    const row = event.target.closest('.table-selection-row');
    if (!row) return;
    
    const rowId = row.id;
    const modal = document.getElementById(`colSelectionModal_${rowId}`);
    const tableSelect = row.querySelector('[name="table[]"]');
    const selectedTable = tableSelect?.value;
    
    if (modal && selectedTable && selectedTable !== "Choose an option") {
      modal.style.display = "block";
    }
  });
  
//   // Add event listener to the merge/display button
//   const displayBtn = document.getElementById('display-merged-table-btn');
//   if (displayBtn) {
//     displayBtn.addEventListener('click', () => dataViewer.displayMergedTable());
//   }
});