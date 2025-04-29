document.addEventListener("DOMContentLoaded", function () {
    initializeForm();
    setupFormSubmission();
});

function initializeForm() {
    const userLoggedIn = get_cookie("logged_in=");
    if (userLoggedIn != "true" || !userLoggedIn) {
        console.warn("User not logged in. Skipping fetchWithAuth.");
        return;
    }
    const data = getSessionData("form-selections");
    if (data) {
        addRow(data.device); //initial row
        populateTestTypeOptions(data.test_type);
        populateVisitNumber(data.visit_num);
    } else {
        fetchWithAuth("/test_tracker/select_options")
        .then(async res => {
            const result = await res.json();
            if (!result) return;
            saveCookie(result, "select_options");
            saveSessionData("form-selections", result);
            addRow(result.device); //initial row
            populateTestTypeOptions(result.test_type);
            populateVisitNumber(result.visit_num);
        })
        .catch(error => console.error("Error fetching select options:", error));
    }
    
}

function populateTestTypeOptions(testTypes) {
    const testTypeElement = document.getElementById('test_type');
    
    // const testTypeSel = document.querySelector("#test_type");
    // if (!testTypeSel) return;

    // testTypeSel.length = 1; // Reset options
    testTypes.forEach(type => {
        const option = document.createElement("option");
        option.value = type;
        option.textContent = type;
        testTypeElement.appendChild(option);
        // testTypeSel.options[testTypeSel.options.length] = new Option(type, type);
    });

    if (testTypeElement) {
      new Choices(testTypeElement, {
        removeItemButton: true,
        placeholderValue: 'Select test type(s)',
        searchPlaceholderValue: 'Search types...',
      });
    }
}

function populateVisitNumber(visitNumbers) {
    const visitNumSel = document.getElementById("visit_number");
    visitNumSel.appendChild(addPlaceholder("Choose an option"));
    if (!visitNumSel) return;

    visitNumSel.length = 1;
    visitNumbers.forEach(type => {
        visitNumSel.options[visitNumSel.options.length] = new Option(type, type);
    })
}

function setupFormSubmission() {
    const userLoggedIn = get_cookie("logged_in=");
    if (userLoggedIn != "true") {
        console.warn("User not logged in. Skipping setupFormSubmission.");
        return;
    }
    const form = document.querySelector("form");
    if (!form) {
        console.error("Form element not found!");
        return;
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent actual form submission

        const jsonData = parseFormToJSON();
        submitFormData(jsonData);
    });
}

function submitFormData(jsonData) {
    fetch("/test_tracker/submit_data", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonData),
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Failed to submit data");
            }
        })
        .then(data => {
            console.log("Data submitted successfully:", data);
            alert("Form submitted successfully!");
            window.location.href = "/test_tracker";
        })
        .catch(error => {
            console.error("Error submitting data:", error);
            alert("Failed to submit form. Please try again.");
        });
}

function addRow(dataOption={}, bodyDataOption={}) {
    console.log('no data?????', dataOption);
    const deviceContainer = document.getElementById("device-container");
    if (!deviceContainer) {
        console.error("Device container not found!");
        return;
    }

    const rowCount = deviceContainer.childElementCount + 1;
    const rowId = `row-${rowCount}`;

    const rowDiv = createRowDiv(rowId, "device-row");
    const device = createRowSelectElement("Device worn?", "device[]", "device", "device-row-element");
    const deviceNum = createRowSelectElement("Device #", "device_num[]", "device device_num", "device-row-element");
    // const bodyPart = createRowSelectElement("Body part detected?", "body_part[]", "device device_body_part");
    const notes = createNotesElement("device-row-element");
    const rmBtn = createRemoveButton(rowId, rowCount, "Remove device");

    // rowDiv.append(device, deviceNum, bodyPart, notes, rmBtn);
    rowDiv.append(device, deviceNum, notes, rmBtn);
    deviceContainer.appendChild(rowDiv);

    populateParentOptions(device.querySelector("select"), dataOption);
    setupDeviceChangeHandler(device.querySelector("select"), deviceNum.querySelector("select"), dataOption);
    // populateBodyPartOptions(bodyPart.querySelector("select"), bodyDataOption);
}


function setupDeviceChangeHandler(deviceSelect, deviceNumSelect, dataOption) {
    deviceSelect.onchange = function () {
        deviceNumSelect.length = 1; // Reset options
        const selectedDevice = this.value;
        const deviceNumList = dataOption[selectedDevice] || [];
        deviceNumList.forEach(num => {
            deviceNumSelect.options[deviceNumSelect.options.length] = new Option(num, num);
        });
    };
}

function populateBodyPartOptions(selectElement, bodyDataOption) {
    bodyDataOption.forEach(bodyPart => {
        selectElement.options[selectElement.options.length] = new Option(bodyPart, bodyPart);
    });
}

function getDeviceOptions() {
    // const selectOptions = get_cookie("select_options=");
    const selectOptions = getSessionData("form-selections");
    return selectOptions ? selectOptions.device : {};
}

// function getBodyPartOptions() {
//     // const selectOptions = get_cookie("select_options=");
//     const selectOptions = getSessionData("form-options");
//     return selectOptions ? JSON.parse(selectOptions).body_part : [];
// }

