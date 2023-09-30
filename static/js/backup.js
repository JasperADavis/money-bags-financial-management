// TOGGLE SWITCH JS

document.getElementById("toggleSwitch").addEventListener("change", function() {
    const form1 = document.getElementById("form1");
    const form2 = document.getElementById("form2");

    if (this.checked) {
        form1.style.display = "none";
        form2.style.display = "block";
    } else {
        form1.style.display = "block";
        form2.style.display = "none";
    }
});
