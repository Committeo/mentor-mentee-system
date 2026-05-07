// =========================
// LOGIN FUNCTION
// =========================
document.addEventListener("DOMContentLoaded", function () {

  const form = document.getElementById("loginForm");

  if (form) {
    form.addEventListener("submit", async function(e){
      e.preventDefault();

      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value.trim();

      if(!email || !password){
        document.getElementById("result").innerText = "Please fill all fields";
        return;
      }

      const data = { email, password };

      try {
        const response = await fetch("http://127.0.0.1:8000/login", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });

        const result = await response.json();

        console.log("Login Response:", result);

        document.getElementById("result").innerText =
          result.message || "Something went wrong";

        if(result.success){

          const user = result.user || result;

          // 🔥 normalize role
          const role = (user.role || "").toLowerCase();

          localStorage.setItem("name", user.name);
          localStorage.setItem("email", user.email);
          localStorage.setItem("dep", user.dep);
          localStorage.setItem("role", role);

          // 🔄 REDIRECT
          if(role === "mentee"){
            window.location.href = "mentee.html";
          } 
          else if(role === "mentor"){
            window.location.href = "mentor.html";
          } 
          else if(role === "admin"){
            window.location.href = "admin.html";
          } 
          else {
            alert("Invalid role: " + role);
          }
        }

      } catch (error) {
        console.error("Error:", error);
        document.getElementById("result").innerText = "Server error";
      }
    });
  }

});


// =========================
// OTP FUNCTION (GLOBAL)
// =========================
async function sendOtp(){

  const email = document.getElementById("email").value.trim();

  if(!email){
    alert("Enter email first");
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:8000/send-otp?email=${email}`, {
      method: "POST"
    });

    const result = await response.json();

    console.log("OTP Response:", result);

    if(result.success){
      alert("OTP sent! Check terminal");
    } else {
      alert(result.message || "Failed to send OTP");
    }

  } catch (error) {
    console.error("OTP Error:", error);
    alert("Server error while sending OTP");
  }
}