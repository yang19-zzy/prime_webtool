function parseFormToJSON() {
    const form = document.querySelector("form");
    const formData = new FormData(form);

    // Parse form metadata
    const metadata = {
        // form_owner: formData.get("form_owner"),
        subject_id: formData.get("subject_id"),
        test_date: formData.get("test_date"),
        // test_id: formData.get("test_id"),
        // test_type: formData.get("test_type"),
        test_type: Array.from(document.getElementById("test_type").querySelectorAll("option"))
            .map(opt => opt.selected ? opt.value : null)
            .filter(value => value !== null),
        visit_number: formData.get("visit_number"),
    };

    // Parse device rows
    const deviceContainer = document.getElementById("device-container");
    const deviceRows = deviceContainer.querySelectorAll(".device-row");
    const devices = Array.from(deviceRows).map(row => {
        return {
            row_id: row.id,
            device_worn: row.querySelector(".device").value,
            device_num: row.querySelector(".device_num").value,
            // body_part: row.querySelector(".device_body_part").value,
            notes: row.querySelector("input[name='notes[]']").value,
        };
    });

    // Combine metadata and devices into a single JSON object
    const result = {
        metadata,
        devices,
    };

    console.log(result);
    return result;
}