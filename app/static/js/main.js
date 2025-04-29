function sayHello() {
    alert("Hello World")
 }



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

function addPlaceholder(msg) {
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.disabled = true;
    // placeholder.hidden = true;
    placeholder.selected = true;
    placeholder.classList.add("placeholder");
    placeholder.textContent = msg;
    return placeholder;
}


function removeRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) row.remove();
}

function saveCookie(obj, name) {
    document.cookie = `${name}=${JSON.stringify(obj)};`;
}

function get_cookie(name) {
    const cookieList = decodeURIComponent(document.cookie).split(';');
    for (let c of cookieList) {
        c = c.trim();
        if (c.startsWith(name)) {
            return c.substring(name.length);
        }
    }
    return "";
}


function createRowDiv(rowId, className) {
    const rowDiv = document.createElement("div");
    rowDiv.className = className;
    rowDiv.id = rowId;
    return rowDiv;
}

function createRowSelectElement(labelText, selectName, selectCls, className, isMulti=false) {
    const elementLabel = document.createElement("label");
    elementLabel.textContent = labelText;

    const elementSelect = document.createElement("select");
    elementSelect.name = selectName;
    if (isMulti) {
        elementSelect.multiple = isMulti;
        elementSelect.classList.add("multi-select");
    } else {
        elementSelect.appendChild(addPlaceholder("Choose an option"));
    }
    elementSelect.classList.add(...selectCls.split(" "));
    const element = document.createElement("div");
    element.classList.add(className);
    element.append(elementLabel, elementSelect);

    return element;
}

function createRowTextElement(labelText, rowId, inputCls, elementCls) {
    const elementLabel = document.createElement("label");
    elementLabel.textContent = labelText;

    const elementInput = document.createElement("input");
    elementInput.type = "text";
    elementInput.classList.add(...inputCls.split(" "));
    elementInput.classList.add(rowId);
    elementInput.readOnly = true;
    elementInput.style.pointerEvents = "none";
    
    const element = document.createElement("div");
    element.classList.add(...elementCls.split(" "));
    element.append(elementLabel, elementInput);

    setTimeout(() => {
        const instance = new Choices(elementInput, {
            removeItemButton: false,
            placeholder: false,
            addItems: true,
            searchEnabled: false,
            duplicateItemsAllowed: false,
            shouldSort: false,
            renderChoiceLimit: -1,
            
        });
        rowChoicesMap[rowId] = instance;
    }, 0);
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

    // if (rowCount > 1) {
    //     rmBtn.onclick = () => removeRow(rowId);
    // } else {
    //     // rmBtn.style.display = "none";
    //     rmBtn.style.visibility = "hidden";
    // }

    rmBtn.onclick = () => removeRow(rowId);

    return rmBtn;
}


function saveSessionData(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
}

function getSessionData(key) {
    return JSON.parse(sessionStorage.getItem(key));
}

function populateParentOptions(selectElement, dataOption) {
    for (const e in dataOption) {
        selectElement.options[selectElement.options.length] = new Option(e, e);
    }
}

function getLastFolderName(path) {
    const parts = path.split('/').filter(Boolean);
    return parts[parts.length - 1];
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


function logoutAndStay() {
    const currentUrl = window.location.href;
    window.location.href = `/logout?state=${encodeURIComponent(currentUrl)}`;
}