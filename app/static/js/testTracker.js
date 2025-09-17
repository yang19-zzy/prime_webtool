class TestTracker {
    constructor() {
        this.trackerSelectOptions = {};
        this.visitNumberSelect = document.getElementById("visit_number");
        this.testTypeSelect = document.getElementById("test_type");
        this.deviceContainer = document.getElementById("device-container");
        this.trackerForm = document.querySelector("form");
        this.trackerSubmitBtn = document.getElementById("tracker-submit-btn");
        this.init();
    }

    init = async () => {
        try {
            if (await isLoggedIn()) {
                this.trackerSelectOptions = await this.getFormOptions();
                if (this.trackerSelectOptions) {
                    this.initializeForm();
                } else {
                    console.error("Failed to load tracker select options.");
                }
            } else {
                console.warn("Not logged in yet.");
            }
        } catch (error) {
            console.error("Initialization error:", error);
        }
    };

    getFormOptions = async () => {
        try {
            const resp = await fetch('/api/data/get/tracker_options', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            if (!resp.ok) throw new Error(`HTTP error! status: ${resp.statusText}`);
            const result = await resp.json();
            return result.tracker_select_options;
        } catch (error) {
            console.error("Error fetching tracker options:", error);
            return null;
        }
    };

    initializeForm = () => {
        this.addRow();
        populateOptions(this.visitNumberSelect, this.trackerSelectOptions.visit_num);
        populateOptions(this.testTypeSelect, this.trackerSelectOptions.test_type);

        new Choices(this.testTypeSelect, {
            removeItemButton: true,
            placeholderValue: 'Select test type(s)',
            searchPlaceholderValue: 'Search types...',
        });

        this.trackerSubmitBtn.addEventListener("click", this.handleFormSubmit);
    };

    addRow = () => {
        const rowCount = this.deviceContainer.childElementCount + 1;
        const rowId = `row-${rowCount}`;
        const rowDiv = createRowDiv(rowId, "device-row");
        const device = createRowSelectElement("Device worn?", "device[]", "device", "device-row-element");
        const deviceNum = createRowSelectElement("Device #", "device_num[]", "device device_num", "device-row-element");
        const notes = createNotesElement("device-row-element");
        const rmBtn = createRemoveButton(rowId, rowCount, "Remove device");

        rowDiv.append(device, deviceNum, notes, rmBtn);
        this.deviceContainer.appendChild(rowDiv);

        const deviceSelect = device.querySelector("select");
        const deviceNumSelect = deviceNum.querySelector("select");
        populateOptions(deviceSelect, this.trackerSelectOptions.device);
        setupDeviceChangeHandler(deviceSelect, deviceNumSelect, this.trackerSelectOptions.device);
    };

    handleFormSubmit = (event) => {
        event.preventDefault();
        const jsonData = this.parseFormToJSON();
        this.submitFormData(jsonData);
    };

    parseFormToJSON = () => {
        const formData = new FormData(this.trackerForm);
        const metadata = {
            subject_id: formData.get("subject_id"),
            test_date: formData.get("test_date"),
            test_type: Array.from(this.testTypeSelect.selectedOptions).map(opt => opt.value),
            visit_number: formData.get("visit_number"),
        };
        const devices = Array.from(this.deviceContainer.querySelectorAll(".device-row")).map(row => ({
            row_id: row.id,
            device_worn: row.querySelector(".device").value,
            device_num: row.querySelector(".device_num").value,
            notes: row.querySelector("input[name='notes[]']").value,
        }));
        return { metadata, devices };
    };

    submitFormData = (jsonData) => {
        fetch("/api/data/action/submit_tracker_form", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(jsonData),
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) throw new Error("Failed to submit data");
            return response.json();
        })
        .then(data => {
            alert("Form submitted successfully!");
            this.trackerForm.reset();
            this.deviceContainer.innerHTML = '';
            this.addRow();
            if (this.testTypeSelect.choices) this.testTypeSelect.choices.clearStore();
        })
        .catch(error => {
            console.error("Error submitting data:", error);
            alert("Failed to submit form. Please try again.");
        });
    };
}

document.addEventListener("DOMContentLoaded", () => {
    new TestTracker();
});

function setupDeviceChangeHandler(deviceSelect, deviceNumSelect, dataOption) {
    deviceSelect.onchange = function () {
        deviceNumSelect.length = 1;
        const deviceNumList = dataOption[this.value] || [];
        deviceNumList.forEach(num => {
            deviceNumSelect.options[deviceNumSelect.options.length] = new Option(num, num);
        });
    };
}
