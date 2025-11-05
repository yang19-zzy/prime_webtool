function toggleNav() {
    const sidenav = document.getElementById("mySidenav");
    const main = document.querySelector(".main-container");
    const showBtn = document.getElementById("menu-show-btn");

    sidenav.classList.toggle("open");
    main.classList.toggle("shifted");

    if (sidenav.classList.contains("open")) {
        showBtn.style.visibility = "hidden";
        showBtn.style.pointerEvents = "none";
    } else {
        showBtn.style.display = "block";
        showBtn.style.visibility = "visible";
        showBtn.style.pointerEvents = "auto";
    }
}

function addPlaceholder(msg, isMulti=false) {
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.disabled = true;
    // placeholder.hidden = true;
    if (isMulti) {
        placeholder.selected = false;
    } else {
        placeholder.selected = true;
    }
    placeholder.classList.add("placeholder");
    placeholder.textContent = msg;
    return placeholder;
}


function removeRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) row.remove();
}


function createRowDiv(rowId, className) {
    const rowDiv = document.createElement("div");
    rowDiv.className = className;
    rowDiv.id = rowId;
    return rowDiv;
}

function createRowSelectElement(labelText, selectName, selectCls, className, isMulti=false, elementId="") {
    const elementLabel = document.createElement("label");
    elementLabel.textContent = labelText;

    const elementSelect = document.createElement("select");
    elementSelect.name = selectName;
    if (isMulti) {
        elementSelect.multiple = isMulti;
        elementSelect.classList.add("multi-select");
        elementSelect.size = 2; // make the dropdown box the same size as single select
        elementSelect.appendChild(addPlaceholder("Double click to modify selection", true));
        elementSelect.disabled = false;
    } else {
        elementSelect.appendChild(addPlaceholder("Choose an option"));
    }
    elementSelect.classList.add(...selectCls.split(" "));
    const element = document.createElement("div");
    element.classList.add(className);
    element.append(elementLabel, elementSelect);
    elementSelect.id = elementId

    return element;
}


function createNotesElement(className) {
    const noteLabel = document.createElement("label");
    noteLabel.textContent = "Other notes?";

    const noteInput = document.createElement("input");
    noteInput.type = "text";
    noteInput.name = "notes[]";
    noteInput.placeholder = "Any notes?";

    const notes = document.createElement("div");
    notes.classList.add(...className.split(" "));
    notes.append(noteLabel, noteInput);

    return notes;
}

function createRemoveButton(rowId, rowCount, title) {
    const rmBtn = document.createElement("button");
    rmBtn.innerHTML = '<i class="fa fa-minus"></i>';
    rmBtn.type = "button";
    rmBtn.classList.add("remove-btn", "btn");
    rmBtn.title = title;

    rmBtn.onclick = () => removeRow(rowId);

    return rmBtn;
}


function populateOptions(selectElement, options) {
    if (!options || Object.keys(options).length === 0) {
      return;
    }
    // console.log("Populating options:", options);
    Object.entries(options).forEach(([key, value]) => {
        // console.log(`Adding option: ${key} with value: ${value}`);
      const option = new Option(key, key);
      selectElement.add(option);
    });
}


function saveSessionData(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
}

function getSessionData(key) {
    return JSON.parse(sessionStorage.getItem(key));
}

async function isLoggedIn() {
    const response = await fetch('/auth/session-check', { method: 'GET', credentials: 'include' });
    return response.ok;
}

function clearCorruptedCache(cookieName) {
  document.cookie = `${cookieName}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
}