// functions to display logged-in user profile
function displayProfile(data) {
    console.log("Data received:", data);
    const profileInfo = data.user_profile;
    console.log("Profile Info:", profileInfo);

    const fields = [
        { id: "profile-firstname", class: "profile-field" },
        { id: "profile-lastname", class: "profile-field" },
        { id: "profile-userid", class: "profile-field" },
        { id: "profile-email", class: "profile-field" },
        { id: "profile-role", class: "profile-field" }
    ];

    const [firstNameDiv, lastNameDiv, userIdDiv, emailDiv, roleDiv] = fields.map(field => {
        const div = document.createElement("div");
        div.id = field.id;
        div.classList.add(field.class);
        return div;
    });

    const [firstNameLabel, firstNameValue] = createProfileField("First Name:", profileInfo.first_name, "profile-field");
    firstNameDiv.appendChild(firstNameLabel);
    firstNameDiv.appendChild(firstNameValue);

    const [lastNameLabel, lastNameValue] = createProfileField("Last Name:", profileInfo.last_name, "profile-field");
    lastNameDiv.appendChild(lastNameLabel);
    lastNameDiv.appendChild(lastNameValue);

    const [userIdLabel, userIdValue] = createProfileField("User ID:", profileInfo.user_id, "profile-field");
    userIdDiv.appendChild(userIdLabel);
    userIdDiv.appendChild(userIdValue);

    const [emailLabel, emailValue] = createProfileField("Email:", profileInfo.email, "profile-field");
    emailDiv.appendChild(emailLabel);
    emailDiv.appendChild(emailValue);

    const [roleLabel, roleValue] = createProfileField("Role:", profileInfo.role, "profile-field");
    roleDiv.appendChild(roleLabel);
    roleDiv.appendChild(roleValue);

    const profileRowName = document.createElement("div");
    profileRowName.classList.add("profile-row");
    profileRowName.appendChild(firstNameDiv);
    profileRowName.appendChild(lastNameDiv);

    const profileRowId = document.createElement("div");
    profileRowId.classList.add("profile-row");
    profileRowId.appendChild(userIdDiv);
    profileRowId.appendChild(emailDiv);

    const profileRowRole = document.createElement("div");
    profileRowRole.classList.add("profile-row");
    profileRowRole.appendChild(roleDiv);

    const profileContainer = document.getElementById("profile-container");
    profileContainer.appendChild(profileRowName);
    profileContainer.appendChild(profileRowId);
    profileContainer.appendChild(profileRowRole);
}

// functions to display user list for admin-user to manage user access
function displayUsers(data) {
    console.log("Data received:", data);
    const users = data.users;
    console.log("Users:", users);

    const userContainer = document.getElementById("profile-manage-container");
    userContainer.innerHTML = "";  // Clear existing content

    // Create table and header
    const table = document.createElement("table");
    table.classList.add("user-table");

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const headers = ["User ID", "First Name", "Last Name", "Email", "Role", "In Lab User?"];
    headers.forEach(text => {
        const th = document.createElement("th");
        th.textContent = text;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    const tbody = document.createElement("tbody");
    users.forEach((user, i) => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td class="center-cell">${user.user_id}</td>
          <td>${user.first_name}</td>
          <td>${user.last_name}</td>
          <td>${user.email}</td>
          <td class="center-cell">${user.role}</td>
          <td class="center-cell">
            <label class="toggle-switch">
              <input type="checkbox" ${user.in_lab_user ? 'checked' : ''} onchange="toggleLabUser('${user.user_id}', ${i})">
              <span class="slider"></span>
            </label>
          </td>
        `
        // const userIdCell = document.createElement("td");
        // userIdCell.textContent = user.user_id;
        // row.appendChild(userIdCell);

        // const firstNameCell = document.createElement("td");
        // firstNameCell.textContent = user.first_name;
        // row.appendChild(firstNameCell);

        // const lastNameCell = document.createElement("td");
        // lastNameCell.textContent = user.last_name;
        // row.appendChild(lastNameCell);

        // const emailCell = document.createElement("td");
        // emailCell.textContent = user.email;
        // row.appendChild(emailCell);

        // const roleCell = document.createElement("td");
        // roleCell.textContent = user.role;
        // row.appendChild(roleCell);

        // const inLabCell = document.createElement("td");
        // inLabCell.textContent = user.in_lab_user ? "Yes" : "No";
        // row.appendChild(inLabCell);

        tbody.appendChild(row);
    });
    table.appendChild(tbody);

    userContainer.appendChild(table);
}

// helper functions
function createProfileField(labelText, valueText, className="profile-field") {
    const label = document.createElement("label");
    label.textContent = labelText;
    label.classList.add(className);

    const value = document.createElement("span");
    value.textContent = valueText || "N/A";

    return [label, value];
}

function toggleLabUser(userId, index) {
    // users[index].in_lab_user = !users[index].in_lab_user;
    // populateTable();
    fetch(`/api/admin/user/${userId}/inlab`, { method: "POST" }).then(() => {
        // Optionally update the UI or state here
        alert(`Toggled in-lab status for user ${userId}`);
    }).catch(console.error);
}

function toggleBtn(userId) {
    const btn = document.getElementById(`toggle-btn-${userId}`);
    if (btn) {
        btn.classList.toggle("active");
    }
    // additional logic to handle user activation/deactivation can be added here
    fetch(`/api/admin/user/${userId}/inlab`, { method: "POST" }).catch(console.error);
    displayUsers();
};

// populate contents when DOM is fully loaded
document.addEventListener("DOMContentLoaded", async function() {
    try {
        const response = await fetch("/api/user/profile");
        const data = await response.json();
        displayProfile(data);

        if (data.user_profile.role === 'admin' || data.user_profile.role === 'dev') {
            try {
                const response = await fetch("/api/admin/users");
                const data = await response.json();
                window.toggleLabUser = toggleLabUser;
                displayUsers(data);
            } catch (error) {
                console.error("Error fetching users:", error);
                alert("Error loading user list. Please visit later or contact admin.");
            }
        }
    } catch (error) {
        console.error("Error fetching profile:", error);
        alert("Error loading profile information. Please visit later or contact admin.");
    }
});