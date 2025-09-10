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
        elementSelect.size = 1; // make the dropdown box the same size as single select
        elementSelect.appendChild(addPlaceholder("Double click to modify selection"));
    } else {
        elementSelect.appendChild(addPlaceholder("Choose an option"));
    }
    elementSelect.classList.add(...selectCls.split(" "));
    const element = document.createElement("div");
    element.classList.add(className);
    element.append(elementLabel, elementSelect);

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

async function isLoggedIn() {
    const response = await fetch('/auth/session-check', { method: 'GET', credentials: 'include' });
    return response.ok;
}