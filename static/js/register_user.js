function validateDetails() {
    var name = document.getElementById("name").value.trim();
    var email = document.getElementById("email").value.trim();
    var password = document.getElementById("password").value;
    var phone = document.getElementById("phone").value;
    var age = document.getElementById("age").value;

    // Validate name
    var nameRegex = /^[a-zA-Z\s]+$/;
    if (!nameRegex.test(name) || name.length === 0) {
        alert("Please enter a valid name with characters and spaces only.");
        return false;
    }

    // Validate email
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email) || !email.endsWith('@gmail.com')) {
        alert("Please enter a valid Gmail address.");
        return false;
    }

    // Validate password
    var passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{10,}$/;
    if (!passwordRegex.test(password)) {
        alert("Please enter a valid password with at least 10 characters, including at least one letter, one number, and one special character.");
        return false;
    }

    // Validate phone number
    var phoneRegex = /^[6-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
        alert("Please enter a valid phone number starting with 6, 7, 8, or 9 and of length 10.");
        return false;
    }

    // Validate age
    var ageNum = parseInt(age);
    if (isNaN(ageNum) || ageNum < 5 || ageNum > 99) {
        alert("Please enter a valid age between 5 and 99.");
        return false;
    }

    return true; // All validations passed
}
