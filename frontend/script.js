const API_URL = "/api/students";


// DOM elements

const studentForm = document.getElementById("student-form");

const nameInput = document.getElementById("name");
const rollNoInput = document.getElementById("roll_no");
const classInput = document.getElementById("student_class");
const marksInput = document.getElementById("marks");
const contactInput = document.getElementById("contact");

const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");

const message = document.getElementById("message");

const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const showAllBtn = document.getElementById("show-all-btn");

const studentTableBody =
    document.getElementById("student-table-body");

const studentCount =
    document.getElementById("student-count");


let editingStudentId = null;


// Load students when page opens

document.addEventListener("DOMContentLoaded", () => {
    loadStudents();
});


// Get all students

async function loadStudents() {

    try {

        const response = await fetch(API_URL);

        const students = await response.json();

        displayStudents(students);

    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to connect to the Flask server.",
            "error"
        );
    }
}


// Display students

function displayStudents(students) {

    studentTableBody.innerHTML = "";

    studentCount.textContent =
        `${students.length} Student${students.length !== 1 ? "s" : ""}`;


    if (students.length === 0) {

        studentTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-message">
                    No students found.
                </td>
            </tr>
        `;

        return;
    }


    students.forEach(student => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${student.id}</td>
            <td>${escapeHTML(student.name)}</td>
            <td>${escapeHTML(student.roll_no)}</td>
            <td>${escapeHTML(student.student_class)}</td>
            <td>${student.marks}</td>
            <td>${escapeHTML(student.contact)}</td>

            <td>
                <button
                    class="edit-btn"
                    onclick="editStudent(${student.id})"
                >
                    Edit
                </button>

                <button
                    class="delete-btn"
                    onclick="deleteStudent(${student.id})"
                >
                    Delete
                </button>
            </td>
        `;

        studentTableBody.appendChild(row);
    });
}


// Add / Update student

studentForm.addEventListener("submit", async function(event) {

    event.preventDefault();


    const studentData = {

        name: nameInput.value.trim(),

        roll_no: rollNoInput.value.trim(),

        student_class: classInput.value.trim(),

        marks: marksInput.value,

        contact: contactInput.value.trim()
    };


    // Validation

    if (
        !studentData.name ||
        !studentData.roll_no ||
        !studentData.student_class ||
        !studentData.marks ||
        !studentData.contact
    ) {

        showMessage(
            "Please fill all fields.",
            "error"
        );

        return;
    }


    if (!/^[A-Za-z\s]+$/.test(studentData.name)) {

        showMessage(
            "Name should contain only letters.",
            "error"
        );

        return;
    }


    if (
        isNaN(studentData.marks) ||
        Number(studentData.marks) < 0 ||
        Number(studentData.marks) > 100
    ) {

        showMessage(
            "Marks must be between 0 and 100.",
            "error"
        );

        return;
    }


    if (!/^\d{10}$/.test(studentData.contact)) {

        showMessage(
            "Contact number must contain exactly 10 digits.",
            "error"
        );

        return;
    }


    try {

        let response;


        if (editingStudentId === null) {

            response = await fetch(API_URL, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(studentData)
            });

        } else {

            response = await fetch(
                `${API_URL}/${editingStudentId}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(studentData)
                }
            );
        }


        const result = await response.json();


        if (!response.ok) {

            showMessage(
                result.error || "Something went wrong.",
                "error"
            );

            return;
        }


        showMessage(
            result.message,
            "success"
        );


        resetForm();

        loadStudents();


    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to connect to the Flask server.",
            "error"
        );
    }
});


// Edit student

async function editStudent(id) {

    try {

        const response =
            await fetch(`${API_URL}/${id}`);

        const student =
            await response.json();


        if (!response.ok) {

            showMessage(
                student.error,
                "error"
            );

            return;
        }


        nameInput.value = student.name;

        rollNoInput.value = student.roll_no;

        classInput.value = student.student_class;

        marksInput.value = student.marks;

        contactInput.value = student.contact;


        editingStudentId = id;


        document.getElementById("form-title").textContent =
            "Update Student";

        submitBtn.textContent =
            "Update Student";

        cancelBtn.style.display =
            "inline-block";


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to load student.",
            "error"
        );
    }
}


// Delete student

async function deleteStudent(id) {

    const confirmed =
        confirm("Are you sure you want to delete this student?");


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(`${API_URL}/${id}`, {
                method: "DELETE"
            });


        const result =
            await response.json();


        if (!response.ok) {

            showMessage(
                result.error,
                "error"
            );

            return;
        }


        showMessage(
            result.message,
            "success"
        );


        loadStudents();

    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to connect to the Flask server.",
            "error"
        );
    }
}


// Search

searchBtn.addEventListener("click", searchStudents);


async function searchStudents() {

    const query =
        searchInput.value.trim();


    if (!query) {

        loadStudents();

        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/search?q=${encodeURIComponent(query)}`
            );


        const students =
            await response.json();


        if (!response.ok) {

            showMessage(
                students.error,
                "error"
            );

            return;
        }


        displayStudents(students);

    } catch (error) {

        console.error(error);

        showMessage(
            "Search failed.",
            "error"
        );
    }
}


// Show all

showAllBtn.addEventListener("click", () => {

    searchInput.value = "";

    loadStudents();

});


// Cancel update

cancelBtn.addEventListener("click", resetForm);


function resetForm() {

    studentForm.reset();

    editingStudentId = null;


    document.getElementById("form-title").textContent =
        "Add Student";

    submitBtn.textContent =
        "Add Student";

    cancelBtn.style.display =
        "none";
}


// Show message

function showMessage(text, type) {

    message.textContent = text;

    message.className = type;


    setTimeout(() => {

        message.textContent = "";

        message.className = "";

    }, 3000);
}


// Prevent HTML injection

function escapeHTML(value) {

    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}