document.addEventListener("DOMContentLoaded", function () {
    new TestValidator();
});



class TestValidator {
    constructor() {
        this.unvalidatedList = [];
        this.validContainer = document.getElementById("validator-container");
        this.init();
    }

    init = async () => {
        try {
            if (await isLoggedIn()) {
                this.unvalidatedList = await this.getUnvalidatedForms();
                if (this.unvalidatedList.length && this.unvalidatedList.length > 0) {
                    this.validContainer.innerHTML = ""; // clear loading message
                    this.renderUnvalidatedForms();
                } else {
                    console.error("No unvalidated forms found.");
                    this.validContainer.innerHTML = "<p class='empty-msg'>No records waiting for confirmation. All set!</p>";
                }
            } else {
                console.warn("Not logged in yet.");
            }
        } catch (error) {
            console.error("Initialization error:", error);
        }
    }

    getUnvalidatedForms = async () => {
        try {
            const resp = await fetch('/api/data/get/unvalidated_forms', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            if (!resp.ok) throw new Error(`HTTP error! status: ${resp.statusText}`);
            const result = await resp.json();
            return result.unvalidated_forms;
        } catch (error) {
            console.error("Error fetching unvalidated forms:", error);
            return [];
        }
    }

    renderUnvalidatedForms = () => {
        this.unvalidatedList.forEach(element => {
            this.createValidationRow(this.validContainer, element);
        });
    }

    createValidationRow(container, item){
        const form_id = item.form_id;
        const form_data = item.data.form_data;
        const form_owner = item.data.form_owner;

        const row = document.createElement('div');
        row.id = form_id;
        row.classList.add("validation-row");

        const subjectId = this.createValidationRowElement(form_data.metadata.subject_id, "Subject ID", "subject-id validation-row-element");
        const testDate = this.createValidationRowElement(form_data.metadata.test_date, "Test Date", "test-date validation-row-element");
        const testType = this.createValidationRowElement(form_data.metadata.test_type, "Test Type(s)", "test-type validation-row-element");
        const submitBy = this.createValidationRowElement(form_owner, "Submit By", "form-owner validation-row-element");
        const confirmBtn = this.createValidationRowBtn(form_id, "btn confirm-btn");

        // console.log(form_data);
        // console.log(item);
        row.append(subjectId, testDate, testType, submitBy, confirmBtn);
        container.appendChild(row);
    }

    createValidationRowElement(data, dataTitle, classList) {
        const element = document.createElement('div');
        element.classList.add(...classList.split(" "));
        const dataList = document.createElement('div');

        if (Array.isArray(data)) {
            data.sort().forEach(item => {
                const span = document.createElement('span');
                span.classList.add('array-item', 'has-data');
                span.textContent = item;
                dataList.appendChild(span);
            });
        } else if (data) {
            const span = document.createElement('span');
            span.textContent = data;
            span.classList.add('has-data');
            dataList.appendChild(span);
        } else {
            const span = document.createElement('span');
            span.textContent = "No data";
            span.classList.add('no-data');
            dataList.appendChild(span);
        }

        element.textContent = `${dataTitle}: `;
        element.append(dataList);
        return element;
    }

    createValidationRowBtn(formId, classList) {
        const btn = document.createElement('button');
        btn.innerHTML = 'Confirm';
        btn.type = 'button';
        btn.classList.add(...classList.split(" "));
        btn.id = `confirm-${formId}`;
        btn.onclick = async () => {
            try {
                const resp = await fetch('/api/data/action/confirm_tracker_form', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ form_id: formId })
                });
                const result = await resp.json();

                if (resp.ok) {
                    const row = document.getElementById(formId);
                    row.style.transition = "transform 0.4s ease-out, opacity 0.4s ease-out";
                    row.style.transform = "translateX(100%)";
                    row.style.opacity = 0;
                    setTimeout(() => this.init(), 300);
                    // setTimeout(() => {
                    //     row.remove();
                        
                    // }, 400);
                } else {
                    console.error("Failed to confirm form:", result.error || result);
                    alert("Failed to confirm. Please try again.");
                }
            } catch (error) {
                console.error("Error fetching unvalidated forms:", error);
                this.validContainer.innerHTML = "<p class='error-msg'>Unable to load data. Please try again later.</p>";
            }
        };
        return btn;
    }

}





// function initializeTrackerList() {
//     const validContainer = document.getElementById("validator-container");

//     const response = fetchWithAuth('/auth/session-check');
//     if (!response || response.status === 401) {
//         console.warn("User not logged in. Skipping fetchWithAuth.");
//         validContainer.innerHTML = "<p class='info-msg'>Please log in to view validation requests.</p>";
//         return;
//     }

//     fetchWithAuth('/test_valid/get_unvalidated_forms')
//         .then(async resp => {
//             const result = await resp.json();
//             const validationList = result.data;
//             validContainer.innerHTML = ""; // clear loading message

//             if (!validationList || validationList.length === 0) {
//                 validContainer.innerHTML = "<p class='empty-msg'>No records waiting for confirmation. All set!</p>";
//             } else {
//                 validationList.forEach(element => {
//                     createValidationRow(validContainer, element);
//                 });
//             }
//         })
//         .catch(error => {
//             console.error("Error fetching unvalidated forms:", error);
//             validContainer.innerHTML = "<p class='error-msg'>Unable to load data. Please try again later.</p>";
//         });
// }



// function createValidationRowBtn(formId, classList) {
//     const btn = document.createElement('button');
//     btn.innerHTML = 'Confirm';
//     btn.type = 'button';
//     btn.classList.add(...classList.split(" "));
//     btn.onclick = async function () {
//         try {
//             const resp = await fetchWithAuth('/test_valid/confirm_form', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify({ form_id: formId })
//             });
//             const result = await resp.json();

//             if (resp.ok) {
//                 const row = document.getElementById(formId);
//                 row.style.transition = "transform 0.4s ease-out, opacity 0.4s ease-out";
//                 row.style.transform = "translateX(100%)";
//                 row.style.opacity = 0;
//                 setTimeout(() => {
//                     row.remove();
//                     setTimeout(() => initializeTrackerList(), 300);
//                 }, 400);
//             } else {
//                 console.error("Failed to confirm form:", result.error || result);
//                 alert("Failed to confirm. Please try again.");
//             }
//         } catch (error) {
//             console.error("Error confirming form:", error);
//             alert("Network error. Please try again.");
//         }
//     };
//     return btn;
// }
